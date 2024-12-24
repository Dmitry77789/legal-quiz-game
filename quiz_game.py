import random
import json
import os
import threading
from colorama import init, Fore, Style

init(autoreset=True)

class Quiz:
    def __init__(self, questions_file="questions.json", scores_file="scores.json"):
        self.questions_file = questions_file
        self.scores_file = scores_file
        self.questions = []
        self.scores = {}
        self.load_questions()
        self.load_scores()

    def load_questions(self):
        try:
            with open(self.questions_file, "r", encoding="utf-8") as file:
                self.questions = json.load(file)
            print(Fore.GREEN + f"Загружено {len(self.questions)} вопросов из '{self.questions_file}'.")
        except FileNotFoundError:
            print(Fore.RED + f"Файл '{self.questions_file}' не найден. Убедитесь, что он находится в текущей директории.")
            self.questions = []
        except json.JSONDecodeError as e:
            print(Fore.RED + f"Ошибка при разборе JSON: {e}")
            self.questions = []

    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r", encoding="utf-8") as file:
                    self.scores = json.load(file)
                print(Fore.GREEN + f"Загружено рекордов из '{self.scores_file}'.")
            except json.JSONDecodeError as e:
                print(Fore.RED + f"Ошибка при разборе JSON в '{self.scores_file}': {e}")
                self.scores = {}
        else:
            self.scores = {}

    def save_scores(self):
        try:
            with open(self.scores_file, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, ensure_ascii=False, indent=4)
            print(Fore.GREEN + f"Рекорды сохранены в '{self.scores_file}'.")
        except Exception as e:
            print(Fore.RED + f"Ошибка при сохранении рекордов: {e}")

    def choose_difficulty(self):
        while True:
            print("\nВыберите уровень сложности:")
            print("1. Легкий")
            print("2. Средний")
            print("3. Сложный")
            choice = input("Ваш выбор (1/2/3): ").strip()
            if choice == "1":
                return "Легкий"
            elif choice == "2":
                return "Средний"
            elif choice == "3":
                return "Сложный"
            else:
                print(Fore.RED + "Неправильный выбор. Пожалуйста, выберите один из доступных вариантов (1, 2 или 3).")

    def show_scores(self):
        if not self.scores:
            print(Fore.YELLOW + "\nТаблица рекордов пуста.\n")
            return
        print(Fore.GREEN + "\nТаблица рекордов:")
        # Создадим список (имя, максимальный балл)
        leaderboard = [(player, max(player_scores)) for player, player_scores in self.scores.items()]
        # Сортируем по максимальному баллу
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        for player, score in leaderboard:
            print(f"{player}: {score} очков")
        print()

    def show_player_stats(self, player_name):
        if player_name not in self.scores:
            print(Fore.YELLOW + "\nНет данных о вашем участии.\n")
            return
        player_scores = self.scores[player_name]
        total_games = len(player_scores)
        average_score = sum(player_scores) / total_games
        highest_score = max(player_scores)
        lowest_score = min(player_scores)
        print(Fore.BLUE + f"\nСтатистика игрока '{player_name}':")
        print(f"Всего игр: {total_games}")
        print(f"Средний балл: {average_score:.2f}")
        print(f"Максимальный балл: {highest_score}")
        print(f"Минимальный балл: {lowest_score}\n")

    def determine_award(self, score, total):
        percentage = (score / total) * 100
        if percentage == 100:
            return Fore.YELLOW + "Золотой Мастер!"
        elif 80 <= percentage < 100:
            return Fore.CYAN + "Серебряный Гений!"
        elif 50 <= percentage < 80:
            return Fore.MAGENTA + "Бронзовый Знаток!"
        else:
            return Fore.RED + "Попробуйте ещё раз!"

    def input_with_timeout(self, prompt, timeout):
        answer = [None]
        def get_input():
            try:
                answer[0] = input(prompt).strip().upper()
            except:
                answer[0] = None

        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True  # Позволяет завершить поток при выходе из программы
        input_thread.start()
        input_thread.join(timeout)
        if input_thread.is_alive():
            return None  # Timeout
        else:
            return answer[0]

    def play_quiz(self, difficulty, player_name):
        # Фильтруем вопросы по сложности
        filtered_questions = [q for q in self.questions if q["difficulty"] == difficulty]
        print(Fore.GREEN + f"\nЗагружено {len(filtered_questions)} вопросов для уровня '{difficulty}'.")

        if len(filtered_questions) < 10:
            print(Fore.YELLOW + f"Внимание: Недостаточно вопросов для выбранного уровня. Доступно {len(filtered_questions)} вопросов.")
            num_questions = len(filtered_questions)
        else:
            num_questions = 10

        random.shuffle(filtered_questions)
        filtered_questions = filtered_questions[:num_questions]  # Ограничиваем до необходимого числа вопросов
        score = 0
        incorrect_questions = []

        for i, question in enumerate(filtered_questions, start=1):
            print(Fore.CYAN + f"\nВопрос {i}: {question['question']}")
            print("У вас есть 30 секунд на ответ. Подумайте и введите правильный вариант.")
            for option in question["options"]:
                print(option)

            # Извлекаем доступные варианты ответов
            valid_options = [option.split('.')[0].strip().upper() for option in question["options"]]

            # Первая попытка
            answer = self.input_with_timeout("Ваш ответ (введите букву): ", 30)

            if answer is None:
                print(Fore.RED + "\nВремя вышло!")
                print(Fore.GREEN + f"Правильный ответ: {question['answer']}")
                print(Fore.YELLOW + f"Объяснение: {question.get('explanation', 'Нет объяснения.')}")
                incorrect_questions.append(question)
                continue

            if answer not in valid_options:
                print(Fore.RED + f"Неверный выбор. Пожалуйста, выберите один из вариантов: {', '.join(valid_options)}.")
                print(Fore.YELLOW + "У вас есть еще одна попытка ввести правильный вариант.")
                
                # Вторая попытка
                second_answer = self.input_with_timeout("Попробуйте еще раз (введите букву): ", 30)

                if second_answer is None:
                    print(Fore.RED + "\nВремя вышло!")
                    print(Fore.GREEN + f"Правильный ответ: {question['answer']}")
                    print(Fore.YELLOW + f"Объяснение: {question.get('explanation', 'Нет объяснения.')}")
                    incorrect_questions.append(question)
                    continue

                if second_answer not in valid_options:
                    print(Fore.RED + f"Неверный выбор снова. Правильный ответ: {question['answer']}")
                    print(Fore.YELLOW + f"Объяснение: {question.get('explanation', 'Нет объяснения.')}")
                    incorrect_questions.append(question)
                    continue
                else:
                    # Проверка второго ответа
                    if second_answer == question["answer"].upper():
                        print(Fore.GREEN + "Правильно!")
                        score += 1
                    else:
                        print(Fore.RED + f"Неправильно! Правильный ответ: {question['answer']}")
                        print(Fore.YELLOW + f"Объяснение: {question.get('explanation', 'Нет объяснения.')}")
                        incorrect_questions.append(question)
            else:
                # Проверка первого ответа
                if answer == question["answer"].upper():
                    print(Fore.GREEN + "Правильно!")
                    score += 1
                else:
                    print(Fore.RED + f"Неправильно! Правильный ответ: {question['answer']}")
                    print(Fore.YELLOW + f"Объяснение: {question.get('explanation', 'Нет объяснения.')}")
                    incorrect_questions.append(question)

        print(f"\nВаш результат: {score}/{num_questions}")
        award = self.determine_award(score, num_questions)
        print(award)

        # Сохранение результатов
        if player_name in self.scores:
            self.scores[player_name].append(score)
        else:
            self.scores[player_name] = [score]

        # Сохранение рекордов
        self.save_scores()

        # Показать таблицу рекордов и статистику игрока
        self.show_scores()
        self.show_player_stats(player_name)

        return score

    def clear_player_stats(self, player_name):
        if player_name in self.scores:
            del self.scores[player_name]
            self.save_scores()
            print(Fore.GREEN + f"Статистика игрока '{player_name}' успешно очищена.")
        else:
            print(Fore.YELLOW + f"Нет статистики для игрока '{player_name}'.")

    def run(self):
        if not self.questions:
            print(Fore.RED + "Нет доступных вопросов для игры. Завершение программы.")
            return

        print(Fore.GREEN + "\nДобро пожаловать в викторину по юридическим понятиям!")

        while True:
            player_name = input("\nВведите ваше имя: ").strip()
            if not player_name:
                print(Fore.RED + "Имя не может быть пустым. Пожалуйста, введите ваше имя.")
                continue
            difficulty = self.choose_difficulty()
            score = self.play_quiz(difficulty, player_name)

            replay = input(Fore.BLUE + "\nХотите сыграть снова? (да/нет): ").strip().lower()
            if replay != "да":
                while True:
                    clear_choice = input(Fore.BLUE + "Хотите очистить вашу статистику? (да/нет): ").strip().lower()
                    if clear_choice == "да":
                        self.clear_player_stats(player_name)
                        break
                    elif clear_choice == "нет":
                        print(Fore.GREEN + "Спасибо за игру! До встречи.")
                        break
                    else:
                        print(Fore.RED + "Неправильный выбор. Пожалуйста, введите 'да' или 'нет'.")
                break

if __name__ == "__main__":
    quiz = Quiz()
    quiz.run()
