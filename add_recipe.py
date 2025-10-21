import streamlit as st
import json
import pandas as pd
from datetime import datetime
import uuid

# Настройки для подавления предупреждений
st.set_option('client.showErrorDetails', False)

def main():
    # Инициализация состояния сессии
    if 'recipes' not in st.session_state:
        try:
            with open('my_recipes.json', 'r', encoding='utf-8') as f:
                st.session_state.recipes = json.load(f)
        except FileNotFoundError:
            st.session_state.recipes = []
    
    # Инициализация временных ингредиентов
    if 'temp_ingredients' not in st.session_state:
        st.session_state.temp_ingredients = []

    st.set_page_config(
        page_title="Мои ПП Рецепты", 
        page_icon="🍳",
        layout="wide"
    )
    
    st.title("📖 База моих рецептов правильного питания")
    st.write("Добавляйте и сохраняйте ваши любимые рецепты здорового питания!")
    
    tab1, tab2 = st.tabs(["📝 Добавить рецепт", "📊 Мои рецепты"])
    
    with tab1:
        final_recipe_form()
    
    with tab2:
        view_recipes_final()

def final_recipe_form():
    st.header("➕ Добавить новый рецепт")
    
    # Секция добавления ингредиентов
    st.subheader("🧂 Добавление ингредиентов")
    
    # Форма для добавления одного ингредиента
    with st.form("add_ingredient_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            ing_name = st.text_input("Название продукта*", placeholder="например: куриная грудка", key="ing_name")
        
        with col2:
            ing_amount = st.number_input("Количество*", min_value=0, value=100, key="ing_amount")
        
        with col3:
            ing_unit = st.selectbox(
                "Единица измерения*", 
                ["г", "мл", "ст.л.", "ч.л.", "шт", "по вкусу"],
                key="ing_unit"
            )
        
        with col4:
            needs_prep = st.checkbox("Нужна предподготовка", key="needs_prep")
        
        # Кнопка добавления ингредиента
        add_clicked = st.form_submit_button("➕ Добавить ингредиент")
        
        if add_clicked:
            if not ing_name:
                st.error("❌ Введите название продукта")
            else:
                # Автоматически ставим прочерк для "по вкусу"
                final_amount = "-" if ing_unit == "по вкусу" else ing_amount
                
                new_ingredient = {
                    "name": ing_name.strip(),
                    "amount": final_amount,
                    "unit": ing_unit,
                    "needs_preparation": needs_prep
                }
                st.session_state.temp_ingredients.append(new_ingredient)
                prep_text = " (нужна предподготовка)" if needs_prep else ""
                st.success(f"✅ Добавлен: {final_amount} {ing_unit} {ing_name}{prep_text}")
    
    # Отображение и редактирование добавленных ингредиентов
    if st.session_state.temp_ingredients:
        st.write("---")
        st.write("#### 📋 Список ингредиентов:")
        
        # Создаем колонки для отображения
        cols = st.columns([4, 2, 2, 2, 1])
        with cols[0]:
            st.write("**Продукт**")
        with cols[1]:
            st.write("**Количество**")
        with cols[2]:
            st.write("**Единица**")
        with cols[3]:
            st.write("**Предподготовка**")
        with cols[4]:
            st.write("**Действие**")
        
        # Отображаем каждый ингредиент с возможностью редактирования
        ingredients_to_remove = []
        for i, ingredient in enumerate(st.session_state.temp_ingredients):
            cols = st.columns([4, 2, 2, 2, 1])
            
            with cols[0]:
                # Поле для редактирования названия
                new_name = st.text_input(
                    "Название", 
                    value=ingredient["name"],
                    key=f"edit_name_{i}",
                    label_visibility="collapsed"
                )
                if new_name != ingredient["name"]:
                    st.session_state.temp_ingredients[i]["name"] = new_name
            
            with cols[1]:
                # Поле для редактирования количества
                if ingredient["unit"] == "по вкусу":
                    st.write("-")
                else:
                    new_amount = st.number_input(
                        "Количество",
                        value=int(ingredient["amount"]) if ingredient["amount"] != "-" else 100,
                        min_value=0,
                        key=f"edit_amount_{i}",
                        label_visibility="collapsed"
                    )
                    if new_amount != ingredient["amount"]:
                        st.session_state.temp_ingredients[i]["amount"] = new_amount
            
            with cols[2]:
                # Выбор единицы измерения
                new_unit = st.selectbox(
                    "Единица",
                    ["г", "мл", "ст.л.", "ч.л.", "шт", "по вкусу"],
                    index=["г", "мл", "ст.л.", "ч.л.", "шт", "по вкусу"].index(ingredient["unit"]),
                    key=f"edit_unit_{i}",
                    label_visibility="collapsed"
                )
                if new_unit != ingredient["unit"]:
                    st.session_state.temp_ingredients[i]["unit"] = new_unit
                    # Автоматически ставим прочерк при выборе "по вкусу"
                    if new_unit == "по вкусу":
                        st.session_state.temp_ingredients[i]["amount"] = "-"
            
            with cols[3]:
                # Чекбокс предподготовки
                new_prep = st.checkbox(
                    "Предподготовка",
                    value=ingredient["needs_preparation"],
                    key=f"edit_prep_{i}",
                    label_visibility="collapsed"
                )
                if new_prep != ingredient["needs_preparation"]:
                    st.session_state.temp_ingredients[i]["needs_preparation"] = new_prep
            
            with cols[4]:
                if st.button("❌", key=f"del_{i}"):
                    ingredients_to_remove.append(i)
        
        # Удаляем отмеченные ингредиенты
        for index in sorted(ingredients_to_remove, reverse=True):
            st.session_state.temp_ingredients.pop(index)
            st.rerun()
    
    # Основная форма рецепта
    st.write("---")
    st.subheader("👨‍🍳 Информация о рецепте")
    
    # Сохраняем текущие значения в session_state чтобы не терять при ошибках
    if 'current_recipe_name' not in st.session_state:
        st.session_state.current_recipe_name = ""
    if 'current_cooking_time' not in st.session_state:
        st.session_state.current_cooking_time = 30
    if 'current_instructions' not in st.session_state:
        st.session_state.current_instructions = ""
    
    with st.form("recipe_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Название рецепта*", 
                placeholder="Салат из киноа с авокадо",
                value=st.session_state.current_recipe_name,
                key="recipe_name"
            )
            cooking_time = st.number_input(
                "Время готовки (мин)*", 
                min_value=1, 
                value=st.session_state.current_cooking_time,
                key="cooking_time"
            )
        
        with col2:
            difficulty = st.selectbox("Сложность", ["легко", "средне", "сложно"], index=0, key="difficulty")
        
        # Множественный выбор категорий
        st.subheader("📂 Категории рецепта")
        categories = st.multiselect(
            "Выберите подходящие категории*",
            ["завтрак", "обед", "ужин", "салат", "суп", "десерт", "перекус"],
            key="categories"
        )
        
        # Инструкция приготовления
        st.subheader("👩‍🍳 Инструкция приготовления")
        instructions = st.text_area(
            "Опишите шаги приготовления*",
            placeholder="Например:\n1. Отварить киноа согласно инструкции\n2. Нарезать авокадо и помидоры\n3. Смешать все ингредиенты\n4. Заправить оливковым маслом",
            height=150,
            value=st.session_state.current_instructions,
            key="instructions"
        )
        
        # Кнопка сохранения рецепта
        submitted = st.form_submit_button("💾 Сохранить рецепт")
        
        if submitted:
            # Сохраняем текущие значения в session_state
            st.session_state.current_recipe_name = name
            st.session_state.current_cooking_time = cooking_time
            st.session_state.current_instructions = instructions
            
            # Валидация данных
            errors = []
            if not name:
                errors.append("❌ Введите название рецепта")
            if not st.session_state.temp_ingredients:
                errors.append("❌ Добавьте хотя бы один ингредиент")
            if not instructions:
                errors.append("❌ Добавьте инструкцию приготовления")
            if not categories:
                errors.append("❌ Выберите хотя бы одну категорию")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Создаем рецепт с уникальным ID
                recipe = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "categories": categories,
                    "difficulty": difficulty,
                    "cooking_time": cooking_time,
                    "ingredients": st.session_state.temp_ingredients.copy(),
                    "instructions": [inst.strip() for inst in instructions.split('\n') if inst.strip()],
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                save_recipe(recipe)
                # Очищаем временные данные
                st.session_state.temp_ingredients = []
                # Очищаем поля формы после успешного сохранения
                st.session_state.current_recipe_name = ""
                st.session_state.current_cooking_time = 30
                st.session_state.current_instructions = ""
                st.success("✅ Рецепт успешно сохранен!")
                st.balloons()

def save_recipe(recipe):
    """Сохраняем рецепт в JSON файл"""
    # Добавляем ID если его нет (для совместимости со старыми рецептами)
    if 'id' not in recipe:
        recipe['id'] = str(uuid.uuid4())
    
    st.session_state.recipes.append(recipe)
    
    with open('my_recipes.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.recipes, f, ensure_ascii=False, indent=2)

def view_recipes_final():
    st.header("📚 Мои рецепты")
    
    if not st.session_state.recipes:
        st.info("🍃 Пока нет сохраненных рецептов. Добавьте первый рецепт!")
        return
    
    # Простые фильтры
    col1, col2 = st.columns(2)
    with col1:
        all_categories = list(set([cat for r in st.session_state.recipes for cat in r.get('categories', [])]))
        category_filter = st.selectbox("Фильтр по категории", ["Все"] + all_categories)
    
    with col2:
        difficulties = ["Все"] + list(set([r['difficulty'] for r in st.session_state.recipes]))
        difficulty_filter = st.selectbox("Фильтр по сложности", difficulties)
    
    # Применяем фильтры
    filtered_recipes = st.session_state.recipes
    if category_filter != "Все":
        filtered_recipes = [r for r in filtered_recipes if category_filter in r.get('categories', [])]
    if difficulty_filter != "Все":
        filtered_recipes = [r for r in filtered_recipes if r['difficulty'] == difficulty_filter]
    
    st.write(f"**Найдено рецептов:** {len(filtered_recipes)}")
    
    for recipe in filtered_recipes:
        categories_text = ", ".join(recipe.get('categories', []))
        with st.expander(f"🍳 {recipe['name']} | ⏱️{recipe['cooking_time']}мин | {recipe['difficulty'].upper()} | {categories_text}"):
            display_recipe_final(recipe)

def display_recipe_final(recipe):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**📦 Категории:** {', '.join(recipe.get('categories', []))}")
        st.write(f"**⚡ Сложность:** {recipe['difficulty']}")
        st.write(f"**⏱️ Время готовки:** {recipe['cooking_time']} мин")
        # Безопасное отображение ID
        if 'id' in recipe:
            st.write(f"**🆔 ID рецепта:** {recipe['id'][:8]}...")
    
    with col2:
        # Подсчет ингредиентов с предподготовкой
        prep_ingredients = [ing for ing in recipe['ingredients'] if ing.get('needs_preparation', False)]
        if prep_ingredients:
            st.write("**⚠️ Ингредиенты с предподготовкой:**")
            for ing in prep_ingredients:
                st.write(f"- {ing['amount']} {ing['unit']} {ing['name']}")
    
    st.write("**🧂 Ингредиенты:**")
    for ing in recipe['ingredients']:
        prep_icon = " ⚠️" if ing.get('needs_preparation', False) else ""
        st.write(f"- **{ing['amount']} {ing['unit']}** {ing['name']}{prep_icon}")
    
    st.write("**👩‍🍳 Приготовление:**")
    for i, step in enumerate(recipe['instructions']):
        st.write(f"{i+1}. {step}")
    
    st.caption(f"📅 Добавлен: {recipe['created_date']}")

if __name__ == "__main__":
    main()