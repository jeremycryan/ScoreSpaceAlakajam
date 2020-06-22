class Score:
    def __init__(self, name, score, index):
        self.name = name
        self.score = score
        self.index = index

    def __eq__(self, other):
        return 0

    def __gt__(self, other):
        if self.score > other.score:
            return True
        elif self.score == other.score and self.index > other.index:
            return True
        else:
            return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        if self.score < other.score:
            return True
        elif self.score == other.score and self.index < other.index:
            return True
        else:
            return False

    def __ge__(self, other):
        return not self.__lt__(other)

    def __str__(self):
        spaces = max(0, 12 - len(self.name)) * " "
        return f"{self.name}:{spaces}{self.score}"


class Scoreboard:

    data = None

    def __init__(self, visible_rows=10, max_rows=200):
        self.visible_rows = visible_rows
        self.max_rows = max_rows
        self.index_count = 0

        self.clear()

    def new_index(self):
        result = self.index_count
        self.index_count += 1
        return result

    def clear(self):
        self.data = [Score("Empty", 0, self.new_index()) for _ in range(self.max_rows)]

    def push(self, name, score):
        new = Score(name, score, self.new_index())
        self.data.append(new)
        self.data.sort(reverse=True)
        self.data = self.data[:self.max_rows]

    def get_visible(self):
        return self.data[:self.visible_rows]

    def get_data(self):
        return self.data[:]

    def __str__(self):
        stringified = [str(item) for item in self.get_visible()]
        return "\n".join(stringified)


if __name__=="__main__":
    a = Scoreboard()
    a.push("Jeremy", 200)
    a.push("Nate", 50)
    a.push("Daniel", 500)
    a.push("Daniel2", 500)
    print(str(a))