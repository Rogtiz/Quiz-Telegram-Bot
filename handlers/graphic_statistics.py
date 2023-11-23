import matplotlib.pyplot as plt


def draw_graphic(total_answers, correct_answers, incorrect_answers):
    categories = ['Общее количество', 'Правильные', 'Неправильные']

    values = [total_answers, correct_answers, incorrect_answers]

    plt.figure(figsize=(8, 4))
    plt.bar(categories, values, color=['blue', 'green', 'red'])

    plt.title('Статистика ответов пользователя')
    plt.ylabel('Количество')

    file_path = '../data/graphic.png'
    plt.savefig(file_path)
