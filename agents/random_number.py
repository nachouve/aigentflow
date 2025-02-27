import random

class RandomNumber:
    def __init__(self):
        self.name = "RandomNumber"

    def run(self, prompt, max_number=100):
        return random.randint(0, max_number)

if __name__ == "__main__":
    import sys
    #print(f"sys.argv: {sys.argv}")
    
    max_number = 100
    if len(sys.argv) > 1:
        try:
            #print(f"sys.argv[1]: {sys.argv[1]}") 
            max_number = int(float(sys.argv[1]))
            #print(f"max_number: {max_number}")  
        except:
            print(f"sys.argv [{sys.argv}].\n")
            print(f"Invalid argument [{sys.argv[1]}]. Using max_number = {max_number}.")
    
    random_number = RandomNumber()
    print(random_number.run("Give me a random number!", max_number=max_number))
