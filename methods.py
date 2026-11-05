lives=3
import main.py as main #main.py is being imported in this command.
import random 
import time
possible_flee_messages_pass=["You tried to run away but failed. The monsters have captured you","You try to flee but you trip. Better luck next time!",""]
formatted=lambda string: string.strip().lower()

class ListError(Exception):
    raise ValueError("The probabilities and items are not equal.")
attributes=("health","strength","speed","name","level","coins","attack power","defense")







probabilities_used=False
permanent_boosts={
    "Tier 1": 1.15,
    "Tier 2": 1.30,
    "Tier 3": 1.40,
}
possible_shop_items=("HP","Strength","X2Stats",)
#Dictionary for the flee probabilities of each monster
flee_probabilities={
    "Skeleton":0.8,
    "Red Dragon":0.75,
    "Headless Horseman": 0.10,
    "Crystal Dragon":0.4,
    "Prime Kyle Walker": 0.0,
    "Green Dragon":0.60,
    "Leviathan":0.10,
    "Megalodon":0.20,

    
}
 #def __init__(self,name:str,health:int,strength:int,speed:int,dodge_rate:float) -> None:
Skeleton=Monster("Skeleton",50,10,20,0.05)
Crystal_Dragon=Monster("Crystal Dragon",150,25,5,0.07)
Prime_Kyle_Walker=Monster("Kyle Walker",90,30,20,0.20)
Green_Dragon=Monster("Green Dragon",105,20,10,0.10)
list_of_monsters=[Skeleton,Crystal_Dragon,Prime_Kyle_Walker,Green_Dragon]




#List of drop rates of each chest
wood_chest=["100G","200G","500G","HP"]
wood_prob=[0.60,0.20,0.13,0.07] #TODO initialize the probabilities of each drop in wood_chest

silver_chest=["250G","500G","1000G","HP","STRENGTH","X2Stats"]
silver_prob=[0.199,0.50,0.15,0.10,0.05,0.001]

gold_chest=["1000G","2500G","5000G","HP","STRENGTH","X2Stats",str(permanent_boosts["Tier 1"])]
gold_prob=[0.10,0.20,0.20,0.20,0.15,0.10,0.05]


chest_dict={
    wood_chest:wood_prob,
    silver_chest:silver_prob,
    gold_chest:gold_prob
    #More to be added soon
}



#result = r.choices(list_name, weights=probabilities_var, k=1)

def open_chest(chest:list,probability:list) -> str:
    """Assigns each chest drop opened a variable"""
    if not isinstance(chest,list) or not isinstance(probability,list):
        raise TypeError("Something went wrong")
    for key in chest_dict:
        list_of_keys=[key]
        if chest not in list_of_keys:
            raise KeyError("The passed argument does not exist. ")
        if not isinstance(probability,list):
            raise TypeError("The probability passed is not a list. ")
        if len(probability)!=len(chest):
            raise ListError
        else:           
            selected_item = random.choices(chest, weights=probability, k=1)[0]
            print(f"You got {selected_item}")
        





def flee_attempt(flee_probabilities:dict,monster_name:str) -> bool:
    roll=float(r.random())
    if roll<flee_probabilities[monster_name]:
        print(f"You have successfully fled from {monster_name}!")

        return True
    else:
        print(f"You tried to run from {monster_name} and failed miserably ")
        lives-=1
        return False
def choose_path(path:set,path_amount:int,)->int:
    
    if not isinstance(path,set):
        raise TypeError("Set of paths is not correct")
    if len(path)<=1:
        raise SyntaxError("Len of paths has to be greater than 1")
    for number in path:
        if not isinstance(number,int):
            raise TypeError("All elements of paths has to numbers")
    else:
        path={i for i in range(1,path_amount+1)}
        
         #This section is under review (L96)
#print(choose_path({1,2,3}))
def shop(price:float,selected_item):
    price=random.randint(100,200)
    buy=input(f"Would you like to buy something from the shop {selected_item}:{price}")
    if buy.formatted()=='y':
        self.coins-=price

        print(f"Shop Item: {selected_item}\n Price: {price}")

        return dict({str(selected_item):float(price)})


    elif buy.formatted()=='n':
        print("Continuing...")
    else:
        print("Invalid answer")
def save_character(character:VideoGame,file_name:str):
    with open(f"{file_name}.txt","a"):
        file.write(class_instance)
        file.close()
        print("File writing done. Character successfully saved.")
#possible_commands=("save character","check stats","exit","access attribute","create new character","delete character")
#attributes=("health","strength","speed","name","level","coins","attack power","defense")

def access_attribute(attribute_name:str,character:VideoGame):
    attribute_name=input("Enter attribute name: ")
    if attribute_name not in attributes:
        raise IndexError("This attribute does not exist")
    else:
        print(f"{attribute_name}:")
        print(f"\n{character.attribute_name()}\n")
    

    

        






















