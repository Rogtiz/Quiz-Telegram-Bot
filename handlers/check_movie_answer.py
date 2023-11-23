import numpy as np


def levenshtein_ratio_and_distance(s, t, ratio_calc=False):
    """ Определяет расстояние Левенштейна между двумя строками.
        Если ratio_calc = True, возвращает отношение сходства между двумя строками. """
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                cost = 1
            distance[row][col] = min(distance[row - 1][col] + 1,  # удаление
                                     distance[row][col - 1] + 1,  # вставка
                                     distance[row - 1][col - 1] + cost)  # замена

    if ratio_calc:
        ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return ratio
    return "Расстояние Левенштейна: {}".format(distance[row][col])


def is_close_enough(user_input, correct_answer, tolerance=0.8):
    """ Проверяет, насколько ввод пользователя близок к правильному ответу, с учетом допустимой погрешности. """
    user_input, correct_answer = user_input.lower(), correct_answer.lower()
    similarity = levenshtein_ratio_and_distance(user_input, correct_answer, ratio_calc=True)
    return similarity > tolerance
