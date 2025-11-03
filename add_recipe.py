import streamlit as st
import json
import pandas as pd
from datetime import datetime
import uuid
import os

# Настройки для подавления предупреждений
st.set_option('client.showErrorDetails', False)

def main():
    # Инициализация состояния сессии
    if 'recipes' not in st.session_state:
        try:
            # Проверяем существует ли файл и не пустой ли он
            if os.path.exists('my_recipes.json') and os.path.getsize('my_recipes.json') > 0:
                with open('my_recipes.json', 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Если файл не пустой
                        st.session_state.recipes = json.loads(content)
                    else:
                        st.session_state.recipes = []
            else:
                st.session_state.recipes = []
        except (json.JSONDecodeError, Exception) as e:
            st.error(f"❌ Ошибка загрузки файла рецептов: {str(e)}")
            st.session_state.recipes = []
            # Создаем пустой файл с корректным JSON
            with open('my_recipes.json', 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    # Инициализация временных ингредиентов
    if 'temp_ingredients' not in st.session_state:
        st.session_state.temp_ingredients = []
    
    # Инициализация имени автора (сохраняется между рецептами)
    if 'saved_author' not in st.session_state:
        st.session_state.saved_author = ""

    st.set_page_config(
        page_title="Рецепты НутринямAI", 
        page_icon="🍳",
        layout="wide"
    )
    
    st.title("📖 Добавление нового рецепта в систему НутринямAI")

    
    tab1, tab2 = st.tabs(["📝 Добавить рецепт", "📊 Мои рецепты"])
    
    with tab1:
        final_recipe_form()
    
    with tab2:
        view_recipes_final()

def final_recipe_form():
    
    # Секция добавления ингредиентов
    st.subheader("Ингредиенты")
    
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
                ["г", "мл", "ст.л.", "ч.л.", "шт", "стакан", "по вкусу"],
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
                    ["г", "мл", "ст.л.", "ч.л.", "шт","стакан", "по вкусу"],
                    index=["г", "мл", "ст.л.", "ч.л.", "шт", "стакан", "по вкусу"].index(ingredient["unit"]),
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
    st.subheader("Рецепт")
    
    # Используем уникальные ключи для полей формы
    form_key = f"recipe_form_{len(st.session_state.recipes)}"
    
    with st.form(form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Название рецепта*", 
                placeholder="Салат из киноа с авокадо",
                key=f"name_{form_key}"
            )
            cooking_time = st.number_input(
                "Время готовки (мин)*", 
                min_value=1, 
                value=30,
                key=f"cooking_time_{form_key}"
            )
        
        with col2:
            # Поле автора с сохраненным значением
            author = st.text_input(
                "Автор рецепта*",
                placeholder="Ваше имя",
                value=st.session_state.saved_author,  # Используем сохраненное имя
                key=f"author_{form_key}"
            )
            difficulty = st.selectbox(
                "Сложность", 
                ["легко", "средне", "сложно"], 
                index=0, 
                key=f"difficulty_{form_key}"
            )
        
        # Одиночный выбор категории - оставляем "-" и добавляем "напитки"
        category = st.selectbox(
            "Выберите категорию",
            ["-", "горячее", "салат", "суп", "закуска", "гарнир", "десерт", "напитки"],
            key=f"category_{form_key}"
        )
        
        # Инструкция приготовления
        st.subheader("Приготовление")
        st.markdown("💡 **Вводите шаги приготовления, каждый шаг с новой строки**")
        
        instructions_input = st.text_area(
            "Опишите шаги приготовления*",
            placeholder="Отварить киноа согласно инструкции\nНарезать авокадо и помидоры\nСмешать все ингредиенты\nЗаправить оливковым маслом",
            height=150,
            key=f"instructions_{form_key}"
        )
        
        # Кнопка сохранения рецепта
        submitted = st.form_submit_button("💾 Сохранить рецепт")
        
        if submitted:
            # Сохраняем имя автора для следующих рецептов
            if author:
                st.session_state.saved_author = author
            
            # Валидация данных
            errors = []
            if not name:
                errors.append("❌ Введите название рецепта")
            if not author:
                errors.append("❌ Введите автора рецепта")
            if not st.session_state.temp_ingredients:
                errors.append("❌ Добавьте хотя бы один ингредиент")
            if not instructions_input:
                errors.append("❌ Добавьте инструкцию приготовления")
            # Убрали проверку на "-" - теперь можно сохранять с любой категорией
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Обрабатываем инструкции - просто разбиваем по строкам
                instructions_list = [step.strip() for step in instructions_input.split('\n') if step.strip()]
                
                # Создаем рецепт с уникальным ID
                recipe = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "author": author,
                    "categories": [category],  # Одна категория в массиве (может быть "-")
                    "difficulty": difficulty,
                    "cooking_time": cooking_time,
                    "ingredients": st.session_state.temp_ingredients.copy(),
                    "instructions": instructions_list,  # Шаги как есть, без цифр
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                save_recipe(recipe)
                # Очищаем временные данные (кроме автора)
                st.session_state.temp_ingredients = []
                st.success("✅ Рецепт успешно сохранен!")
                st.balloons()
                # Перезагружаем страницу для очистки полей формы
                st.rerun()

def save_recipe(recipe):
    """Сохраняем рецепт в JSON файл"""
    # Добавляем ID если его нет (для совместимости со старыми рецептами)
    if 'id' not in recipe:
        recipe['id'] = str(uuid.uuid4())
    
    st.session_state.recipes.append(recipe)
    
    # Сохраняем в локальный файл
    try:
        with open('my_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.recipes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ Ошибка сохранения рецепта: {str(e)}")

def delete_recipe(recipe_id):
    """Удаляем рецепт по ID"""
    try:
        # Находим индекс рецепта
        recipe_index = next((i for i, r in enumerate(st.session_state.recipes) if r['id'] == recipe_id), None)
        
        if recipe_index is not None:
            # Удаляем рецепт из session state
            deleted_recipe = st.session_state.recipes.pop(recipe_index)
            
            # Сохраняем обновленные данные в файл
            with open('my_recipes.json', 'w', encoding='utf-8') as f:
                json.dump(st.session_state.recipes, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ Рецепт '{deleted_recipe['name']}' успешно удален!")
            st.rerun()
        else:
            st.error("❌ Рецепт не найден")
    except Exception as e:
        st.error(f"❌ Ошибка при удалении рецепта: {str(e)}")

def clear_all_recipes():
    """Очищаем все рецепты после скачивания"""
    try:
        # Сохраняем количество рецептов для сообщения
        recipes_count = len(st.session_state.recipes)
        
        # Очищаем рецепты
        st.session_state.recipes = []
        
        # Очищаем файл
        with open('my_recipes.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ Все рецепты ({recipes_count} шт.) успешно скачаны и очищены!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Ошибка при очистке рецептов: {str(e)}")

def view_recipes_final():
    st.header("📚 Записанные рецепты")
    
    if not st.session_state.recipes:
        st.info("🍃 Пока нет сохраненных рецептов. Добавьте первый рецепт!")
        return
    
    # Кнопка скачивания всех рецептов с автоматической очисткой
    if st.session_state.recipes:
        try:
            json_data = json.dumps(st.session_state.recipes, ensure_ascii=False, indent=2)
            
            # Создаем состояние для отслеживания скачивания
            if 'download_triggered' not in st.session_state:
                st.session_state.download_triggered = False
            
            # Кнопка скачивания, которая запускает очистку
            if st.download_button(
                label="📥 Скачать рецепты и очистить",
                data=json_data,
                file_name=f"my_recipes_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                help="Скачайте JSON файл со всеми рецептами, после чего база очистится автоматически",
                key="download_and_clear"
            ):
                # Устанавливаем флаг что скачивание произошло
                st.session_state.download_triggered = True
            
            # Если скачивание произошло, очищаем рецепты
            if st.session_state.download_triggered:
                clear_all_recipes()
                # Сбрасываем флаг после очистки
                st.session_state.download_triggered = False
                
        except Exception as e:
            st.error(f"❌ Ошибка создания файла для скачивания: {str(e)}")
    
    # Отображаем все рецепты без фильтров
    st.write(f"**Всего рецептов:** {len(st.session_state.recipes)}")
    
    for i, recipe in enumerate(st.session_state.recipes):
        # Для совместимости со старыми рецептами (где categories мог быть массивом)
        if isinstance(recipe.get('categories'), list) and recipe['categories']:
            categories_text = recipe['categories'][0] if len(recipe['categories']) > 0 else "Не указано"
        else:
            categories_text = recipe.get('categories', 'Не указано')
            
        with st.expander(f"🍳 {recipe['name']} | 👤{recipe.get('author', 'Неизвестно')} | ⏱️{recipe['cooking_time']}мин | {recipe['difficulty'].upper()} | {categories_text}"):
            
            # Кнопка удаления рецепта
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ Удалить рецепт", key=f"delete_{i}", type="secondary"):
                    delete_recipe(recipe['id'])
            
            display_recipe_final(recipe)

def display_recipe_final(recipe):
    # Для совместимости со старыми рецептами
    if isinstance(recipe.get('categories'), list) and recipe['categories']:
        categories_text = recipe['categories'][0] if len(recipe['categories']) > 0 else "Не указано"
    else:
        categories_text = recipe.get('categories', 'Не указано')
        
    st.write(f"**Автор:** {recipe.get('author', 'Неизвестно')}")
    st.write(f"**Категория:** {categories_text}")
    st.write(f"**Сложность:** {recipe['difficulty']}")
    st.write(f"**⏱Время готовки:** {recipe['cooking_time']} мин")
    
    st.write("**Ингредиенты:**")
    for ing in recipe['ingredients']:
        prep_icon = " ⚠️" if ing.get('needs_preparation', False) else ""
        st.write(f"- **{ing['amount']} {ing['unit']}** {ing['name']}{prep_icon}")
    
    st.write("**Приготовление:**")
    for i, step in enumerate(recipe['instructions']):
        st.write(f"{i+1}. {step}")
    
    st.caption(f"Добавлен: {recipe['created_date']}")

if __name__ == "__main__":
    main()