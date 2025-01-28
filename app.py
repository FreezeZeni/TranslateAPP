# type: ignore
import flet as ft
import win32api
import win32con
import time
import keyboard
import threading
import win32gui
import asyncio
from deep_translator import GoogleTranslator
import speech_recognition as sr
import queue

translation_language = 'en'
mode = 0
voice_mode = -1
is_recognition_active = True


def listen_in_background(recognizer, source, audio_queue):
    global is_recognition_active
    while True:
        if is_recognition_active:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=None)
                audio_queue.put(audio)
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"Ошибка записи: {e}")
                time.sleep(1)
        else:
            time.sleep(0.5)

def process_audio(recognizer, audio_queue):
    global is_recognition_active, textbar
    while True:
        if is_recognition_active and not audio_queue.empty():
            audio = audio_queue.get()
            try:
                text = recognizer.recognize_google(audio, language="ru-RU")
                print(f"Распознано: {text}")
                textbar.value=text
                textbar.update()
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Ошибка сервиса: {e}")
                time.sleep(1)
        else:
            time.sleep(0.5)

def toggle_recognition():
    global is_recognition_active
    is_recognition_active = not is_recognition_active
    state = "включено" if is_recognition_active else "выключено"
    print(f"Распознавание {state}")

def voice():
    recognizer = sr.Recognizer()
    audio_queue = queue.Queue()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Начало распознавания речи. Для выхода нажмите Ctrl+C")
        print("Нажмите Enter, чтобы включить/выключить распознавание")

        listen_thread = threading.Thread(target=listen_in_background, 
                                      args=(recognizer, source, audio_queue))
        process_thread = threading.Thread(target=process_audio, 
                                       args=(recognizer, audio_queue))
        
        listen_thread.daemon = True
        process_thread.daemon = True
        
        listen_thread.start()
        process_thread.start()
        
        try:
            while True:
                input()  # Ожидание нажатия Enter
                toggle_recognition()
        except KeyboardInterrupt:
            print("\nЗавершение работы...")


def Open_a_chat():
    global mode
    
    if mode == 1:
        key_code = 0x59
    elif mode == 2:
        key_code = 0x55
    else:
        key_code = 0x54
    
    win32api.keybd_event(key_code, 0, 0, 0)
    time.sleep(0.02)
    
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

def type_text(text):
    for char in text:
        keyboard.press(char)
        time.sleep(0.01)
        keyboard.release(char)
        time.sleep(0.01)
        
def translate_text(text):
    global translation_language
    
    translator = GoogleTranslator(source='ru', target=translation_language)
    translated = translator.translate(text)
    return translated

def on_hotkey():
    global textbar, history, text, mode_ap, slider_count
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    time.sleep(0.01)
    win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
    
    time.sleep(0.01)
    win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.01)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    

    
    switch_keyboard_layout('00000409')
    

    if mode_ap.value == 'Спам':
        for repetition in range(0, int(slider_count.value)):
            time.sleep(0.1)
            
            Open_a_chat()
            
            time.sleep(0.1)
            
            type_text(text.value)
            
            time.sleep(0.1)
            
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
    else:
        time.sleep(0.1)  
        Open_a_chat()
        
        time.sleep(0.1)
        
        type_text(text.value)

        time.sleep(0.1)
        switch_keyboard_layout('00000419')
    
    
    if history.value == '':
        history.value += str(textbar.value)
        history.update()
    else:
        history.value += str(f'\n{textbar.value}')
        history.update()
    
    text.value = ""
    text.update()
    textbar.value = ""
    textbar.update()
    

def switch_keyboard_layout(layout_hex):
    hwnd = win32gui.GetForegroundWindow()
    layout_id = int(layout_hex, 16)
    win32api.PostMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, layout_id)

def main(page: ft.Page):
    global textbar, history, text, mode_ap, slider_count
    page.title = "Переводчик Винкс"
    page.window.width = 840
    page.window.height = 400
    page.window.center()
    
    async def on_click_up(e):
        textbar.value = textbar.value.upper()
        textbar.update()
        
        text.value = text.value.upper()
        text.update()
        
        # Анимация уменьшения размера, изменения цвета и вращения
        upper_button.width = 30
        upper_button.height = 30
        upper_button.bgcolor = ft.Colors.TRANSPARENT
        upper_button_image.rotation = 0.2
        upper_button.update()
        
        # Возвращение к исходным параметрам с задержкой
        await asyncio.sleep(0.1)
        upper_button.width = 40
        upper_button.height = 40
        upper_button.bgcolor = ft.Colors.BLUE_200
        upper_button_image.rotation = 0
        upper_button.update()

    async def on_click_down(e):
        # Применяем upper() ко всему тексту в textbar
        textbar.value = textbar.value.lower()
        textbar.update()  # Обновляем textbar на странице
        
        # Переводим текст в textbar и обновляем text
        text.value = text.value.lower()
        text.update()  # Обновляем text на странице
        
        # Анимация уменьшения размера, изменения цвета и вращения
        lower_button.width = 30
        lower_button.height = 30
        lower_button.bgcolor = ft.Colors.TRANSPARENT
        lower_button_image.rotation = 0.2
        lower_button.update()
        
        # Возвращение к исходным параметрам с задержкой
        await asyncio.sleep(0.1)
        lower_button.width = 40
        lower_button.height = 40
        lower_button.bgcolor = ft.Colors.BLUE_200
        lower_button_image.rotation = 0
        lower_button.update()

    upper_button_image = ft.Image(
        src=r"ICONS\64_up.png",  # Замените на путь к вашему изображению
        width=24,
        height=24,
        fit=ft.ImageFit.CONTAIN,
        animate_rotation=ft.animation.Animation(
            duration=100,
            curve=ft.AnimationCurve.EASE_IN_OUT
            )
    )

    lower_button_image = ft.Image(
        src=r"ICONS\64_down.png",  # Замените на путь к вашему изображению
        width=24,
        height=24,
        fit=ft.ImageFit.CONTAIN,
        animate_rotation=ft.animation.Animation(
            duration=100,
            curve=ft.AnimationCurve.EASE_IN_OUT
            )
    )

        # Создание контейнера с изображением и комплексной анимацией
    upper_button = ft.Container(
        content=upper_button_image,
        width=40,
        height=40,
        padding=5,
        alignment=ft.alignment.center,
        on_click=on_click_up,
        border_radius=ft.border_radius.all(5),
        bgcolor=ft.Colors.BLUE_200,
        animate=ft.animation.Animation(
            duration=250,  # Длительность анимации в миллисекундах
            curve=ft.AnimationCurve.EASE_IN_OUT
            )
    )
    
    # Создание контейнера с изображением и комплексной анимаций
    lower_button = ft.Container(
        content=lower_button_image,
        width=40,
        height=40,
        padding=5,
        alignment=ft.alignment.center,
        on_click=on_click_down,
        border_radius=ft.border_radius.all(5),
        bgcolor=ft.Colors.BLUE_200,
        animate=ft.animation.Animation(
            duration=250,  # Длительность анимации в миллисекундах
            curve=ft.AnimationCurve.EASE_IN_OUT
            )
    )
    
    voice_button_image = ft.Image(
        src=r"ICONS\64_voice.png",
        width=24,
        height=24,
        fit=ft.ImageFit.CONTAIN
    )
    
    def on_click_voice(e=None):
        global voice_mode

        if voice_mode == 0:
            voice_mode = 1
            voice_button_image.src=r"ICONS\64_voice_on.png"
            voice_button.update()
            toggle_recognition()
        elif voice_mode == -1:
            voice_mode = 1
            voice_button_image.src=r"ICONS\64_voice_on.png"
            voice_button.update()
            voice()
        else:
            voice_mode = 0
            voice_button_image.src=r"ICONS\64_voice.png"
            voice_button.update()
            toggle_recognition()
    
    voice_button = ft.Container(
        content=voice_button_image,
        width=40,
        height=40,
        padding=5,
        alignment=ft.alignment.center,
        on_click=on_click_voice,
        border_radius=ft.border_radius.all(5),
        bgcolor=ft.Colors.BLUE_200
    )
    
    def dropdown_changed(e):
        global translation_language
        
        if language_menu.value == 'Немецкий':
            translation_language = 'de'
        elif language_menu.value == 'Французкий':
            translation_language = 'fr'
        else:
            translation_language = 'en'

    def mode_changed(e):
        global mode
        
        if chat_mode.value == 'Коммандный':
            mode = 1
        elif chat_mode.value == 'Групповой':
            mode = 2
        else:
            mode = 0

    language_menu = ft.Dropdown(
        on_change=dropdown_changed,
        value="Английский",
        options=[
            ft.dropdown.Option("Английский"),
            ft.dropdown.Option("Немецкий"),
            ft.dropdown.Option("Французкий"),
        ],
        width=200,
    )
    
    chat_mode = ft.Dropdown(
        on_change=mode_changed,
        value="Общий",
        options=[
            ft.dropdown.Option("Общий"),
            ft.dropdown.Option("Коммандный"),
            ft.dropdown.Option("Групповой")
        ],
        width=200, 
    )
    def slider_changed(e):
        slider_count.value = f"{int(e.control.value)}"
        page.update()
    
    slider_count = ft.Text(size=18)
    def spam_or_translate(e, language_menu):
        
        if mode_ap.value == 'Спам' and len(row.controls) == 5:
            del row.controls[1:2]
            row.controls.append(
                ft.Slider(min=0, max=10, divisions=10, on_change=slider_changed)
            )
            row.controls.append(
                slider_count
            )
            page.update()
            
        elif mode_ap.value == 'Переводчик' and len(row.controls) == 6:
            del row.controls[4:6]
            row.controls.insert(1, language_menu)
            page.update()
            
    mode_ap = ft.Dropdown(
        on_change=lambda e: spam_or_translate(e, language_menu),
        value="Переводчик",
        options=[
            ft.dropdown.Option("Переводчик"),
            ft.dropdown.Option("Спам")
        ],  
        width=165,
    )
    
    row = ft.Row([mode_ap, language_menu, chat_mode, upper_button, lower_button, voice_button])
    
    history = ft.TextField(
        label="История",
        multiline=True,
        min_lines=1,
        max_lines=6
    )
    
    def textbox_changed(e):
        if mode_ap.value == 'Переводчик':
            text.value = e.control.value
            text.value = translate_text(text.value)
            page.update()
        else:
            text.value = e.control.value
    
    text = ft.Text(value="")
    textbar = ft.TextField(
        label="Введите текст...",
        on_change=textbox_changed,
        on_focus=lambda e: keyboard.add_hotkey('enter', lambda: threading.Thread(target=on_hotkey).start()),
        on_blur=lambda e: keyboard.unhook_all_hotkeys()
    )

    
    page.add(row, textbar, text, history)


if __name__ == '__main__':
    ft.app(target=main)
