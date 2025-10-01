import random

class IDGenerator:
    def __init__(self):
        # Store generated IDs to prevent duplicates
        self.generated_ids = set()

    def generate_id(self, type_digit: int, length: int) -> int:
        if type_digit < 1 or type_digit > 9:
            raise ValueError("type_digit must be between 1 and 9")

        if length < 2:
            raise ValueError("length must be at least 2 (1 type digit + >=1 random digit)")

        while True:
            # how many digits remain after the type digit
            remaining_digits = length - 1

            # max random value with that many digits
            max_value = 10 ** remaining_digits - 1

            random_digits = random.randint(0, max_value)

            # zero-pad the random part
            new_id = int(f"{type_digit}{random_digits:0{remaining_digits}d}")

            if new_id not in self.generated_ids:
                self.generated_ids.add(new_id)
                return new_id