import unittest
from virus_war_bot import VirusWarGame


class TestStringMethods(unittest.TestCase):
    def test_no_move(self):
        init = """1303444222
1330244422
3300244444
3302444402
3333340002
3133004442
3133033000
3313300000
1133030000
1330000000"""
        self.assertEquals(init, VirusWarGame(init, 1).go())

    def test_one_variant(self):
        init = """1103342222
                  1113342222
                  1113342222
                  1103342222
                  1000040222
                  1100344444
                  1101344002
                  1110100022
                  1110000044
                  1111114444"""

        result = """1103342222
1113342222
1113342222
1103342222
1000040222
1100344444
1101344004
1110100044
1110000044
1111114444"""

        self.assertEquals(result, VirusWarGame(init, 1).go())

    def test_game_ends(self):
        field = """0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000
                   0000000000"""
        prev_field = ''
        for i in range(0, 1000):
            if i % 2 == 0:
                player = 2
            else:
                player = 1
            game = VirusWarGame(field, player)
            result = game.go()
            if result == prev_field:
                break
            prev_field = field
            field = result
        else:
            self.fail("game doesn't end for 1000 rounds")


if __name__ == '__main__':
    unittest.main()
