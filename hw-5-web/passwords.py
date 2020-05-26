import random


class PasswordSettings:
    def __init__(self, length=20, use_lowercase=True, use_uppercase=True, use_numbers=True, use_special=True,
                 min_numbers=1, min_special=1):
        self.length = length
        self.use_lowercase = use_lowercase
        self.use_uppercase = use_uppercase
        self.use_numbers = use_numbers
        self.use_special = use_special
        self.min_numbers = min_numbers
        self.min_special = min_special

    def is_valid(self):
        if not self.use_lowercase and not self.use_uppercase and not self.use_numbers and not self.use_special:
            return False
        min_numbers = self.min_numbers if self.use_numbers else 0
        min_special = self.min_special if self.use_special else 0
        return self.length > 0 and self.length >= min_numbers + min_special


class PasswordGenerator:
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    special = '!@#$%^*()-+='

    def generate(self, settings):
        reserved = list()
        if settings.use_numbers:
            for i in range(0, settings.min_numbers):
                reserved.append(random.choice(self.numbers))
        if settings.use_special:
            for i in range(0, settings.min_special):
                reserved.append(random.choice(self.special))
        password = [None] * settings.length
        positions = random.sample(range(settings.length), len(reserved))
        for i in range(len(positions)):
            password[positions[i]] = reserved[i]

        population = list(filter(lambda x: x is not None, [
            self.lowercase if settings.use_lowercase else None,
            self.uppercase if settings.use_uppercase else None,
            self.numbers if settings.use_numbers else None,
            self.special if settings.use_special else None,
        ]))
        all_s = sum(len(s) for s in population)
        weights = [len(s) / all_s for s in population]

        for i in range(settings.length):
            if password[i] is None:
                chars = random.choices(population, weights)[0]
                password[i] = random.choice(chars)

        return ''.join(password)
