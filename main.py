#Imports the @abstractmethod used in the health abstract method
import time as wait
import methods.py as methods
import numpy as np
from types import MappingProxyType as map #map makes sure thedictionary is immutable to prevent cheating
import random
formatted=lambda: x.strip().lower()
possible_commands=("save character","check stats","exit","access attribute","create new character","delete character")
rewards=dict({
    "Skeleton":random.randint(50,100)
})
shop_instance=shop(random.randint(200,300),random.choice(list(possible_shop_items)))

class InvalidInputError(Exception):
    raise ValueError("Invalid Input. Something went wrong.")

class LevelError(Exception):
    
    raise ValueError("Level is an invalid integer. Level must be only between 1 and 10.")
class InvalidStatsError(Exception):
    
    raise TypeError("One or more parameters are invalid. Fix your input and try again stupid.")
class CrashError(Exception):
    
    raise SystemError("Something went wrong while computing your answer. Please restart your python file.")
class CrashProgram(Exception):
    raise SystemExit("Exiting system")
class InvalidKeyValuePair(Exception):
    raise KeyError("The key you entered is incorect and does not exist. Error found at",{key})


class VideoGame:
    def __init__(self,health:int,strength:int,speed:int,level:int,name:str,coins:int,attack_power:float,defense:float) -> None:
        """Initialize the properties of the class"""
        self.health=100
        self.strength=strength
        self.speed=speed
        self.level=1
        self.name="Cole Palmer"
        self.coins=0
        self.attack_power=10
        self.defense=10
        
    
    def take_damage(self,amount:float):

        self.health-=amount
        print("Ouch")
        
        return health
    def attack(self,target):
        damage=self.attack_power
        target.take_normal_damage(damage)
    @health.setter
    def health(self,health):
        """Sets the health attribute"""
        if health>100:
            health==100
        elif health<=0:   
            health==1    
        else:
            health=self._health
    @property
    def strength(self,strength)->None:
        """Abstract method for strength attribute"""
        strength=self.strength
        return strength
    def take_damage1(self,health,damage):
        pass
    @property
    def level(self,level)->None:
        """Abstract method for level attribute"""
        level=self.level
        return level
    def level_up(self,level):
        level+=1
        health+=10
        speed+=5
        attack_power+=2
        coins+=random.randint(100,300)
    @level.setter
    def level(self,level):
        """Sets the level attribute"""
        if level<1 or level>10:
            raise LevelError
        else:
            self.level=level
    def attack(self,target_monster):
        damage_hero=self.attack_power
        target_monster.take_damage(damage_hero)


    @property
    def coins(self,coins):
        """Abstract method for coins"""
        coins=self.coins
        return coins
    @coins.setter
    def coins(self,coins):
        if coins<0:
            coins==0
        elif not isinstance(coins,int):
            raise TypeError("Invalid coins type")
        else:
            self.coins==coins

    def __str__(self):
        #health, strength, speed, level, name are paramaters of __init__
        return f"Health: {health}n\
                Strength: {strength}n\
                Speed: {speed}n\
                Level: {level}n\
                Name: {name}n\
                "
class Monster:
    def __init__(self,name:str,health:int,strength:int,speed:int,dodge_rate:float,attack_power:float) -> None:
        self.name:str=name
        self.health:int=health
        self.strength:int=strength
        self.speed:int=speed
        self.dodge_rate:float=dodge_rate
        self.attack_power:float=attack_power
    
    def take_damage(self,damage):
        actual_damage = max(0, damage - self.defense)
        self.health-=actual_damage
    

    @property
    def name(self,name):
        return self.name

        return self.name
    def take_normal_damage(self,amount):
        self.health-=1
    @property
    def health(self,health):
        return self.health
        return self.health
    @health.setter
    def health(self,health):
        if not isinstance(health,int):
            raise TypeError("Invalid Health")
        if health>2000:
            health==2000
        if health<0:
            health=1
        else:
            health=self.health
    @property
    def name(self,name):
        return self.name
    @name.setter
    def name(self,name):
        disallowed="!@#$%^&*()+=/<>:\][]"

        if not isinstance(name,str):
            raise TypeError
        if len(name)>50:
            raise ValueError("Name is too long")
        if name in disallowed:
            raise ValueError("Invalid Name")
        else:
            name=self.name
    @property
    def dodge_rate(self,dodge_rate:float):
        return self.dodge_rate
    def __str__(self):
        return ""
    def attack(self,attack_power):
        pass

    

    
    try:
        input_name=str(input("Enter name"))
        input_level=int(input("Enter level (#)"))
        input_strength=int(input("Enter strength (#)"))
        input_speed=int(input("Enter speed (#)"))
    except ValueError or TypeError as e:
        print("Try again stupid.")
        i=input("Would you like to try again? (y/n)")
        if i.formatted()=='y':
            input_speed=int(input("Enter speed (#)"))
            input_strength=int(input("Enter strength (#)"))
            input_name=str(input("Enter name"))
            input_level=int(input("Enter level (#)"))
        elif i.formatted()=='n':
            print("Exiting system")
            wait.sleep(1)
            raise SystemExit
        else:
            pass
            raise CrashError

    finally:
        print("Input executed | Waiting further authorization")
    #health, strength, speed, level, name are paramaters of __init__
        wait

    class_instance=VideoGame(input_health,input_level,input_strength,input_speed,input_name)
    print("Loading...")
    
    wait.sleep(1.3)

    print(class_instance.__str__())
    class_dict={
        f"{class_instance.name}":class_instance
        
    }
    def del_dict(class_dict,input_4):
        deleted_instance=input("Which instance would you like to delete? (name the key of it)")
        for key in class_dict:
            if deleted_instance==key:
                del class_dict[deleted_instance]
            else:

                raise InvalidKeyValuePair
    def create_character(input_2:str) -> None:
        input_2=input("Would you like to create another character? (y/n)")
        if input_2.formatted()=="y":
            input_speed=int(input("Enter speed (#)"))
            input_health=int(input("Enter health (#)"))
            input_level=int(input("Enter health (#)"))
            input_name=str(input("Enter name"))
            new_char=VideoGame(input_speed,input_health,input_level,input_name)
    
            

            class_dict.append({"Character": new_char})
            return new_char
    print("You venture through a vast and magical forest. The air is humid and the weather is cold but sunny. You can hear birds chirp and twigs snap on the leafy floor.")
    print("You come accross a fork in the forest trail. Pick wisely.")
    input=input("Which path do you take (1,2)")
    chosen_path=methods.choose_path(path={1,2},path_amount=2)
    skelly_path=int(random.choice(chosen_path))

    if input.formatted()==skelly_path:
        skeleton=input("You come accross a pack of skeletons in a forest clearing. You observe them play in a small river; however, they see you and one of them stays to fight you. Do you fight or run?")
        if skeleton.formatted()=='flee':

            methods.flee_attempt(flee_methods,"Skeleton")
            
        
    else:
        crystal_dragon=input("You come accross a cave and you see a dragon covered in crystals resting over a chest. Do you choose to fight or run away?")
        if crystal_dragon.formatted=='flee':
            methods.flee_attempt(flee_methods,"Crystal Dragon")
        else:
            while class_instance.health>0 and Crystal_Dragon.health>0:
                class_instance.attack()
                wait(2.0)
                Crystal_Dragon.attack()
                if class_instance.health<=0:
                    print("The battle is over.")
                    lives-=1
                elif Crystal_Dragon.health<=0 and class_instance.health>0:
                    print("You won!")
                    
                    shop_instance()
    print("There is a hill covered in trees while a cool wind blows down the October leaves. You climb up.")
    wooden_chest_input=input(("You continue to adventure when you come accross a small wooden chest lying on top of a rock. Do you try to open it or not."))
    if wooden_chest_input.formatted()=='y':
        methods.open_chest(wood_chest,wood_prob)
        print(f"You got {selected_item}!")

        if selected_item[-1]=="G":
            class_instance.coins+=int(selected_item[:-1])
        elif selected_item=="HP":
            class_instance.health+=random.randint(10,25)
        
    if wooden_chest_input.formatted()=='n':
        print("You ignore the wooden chest. Bummer.")
    rest_on_boulder=input(("You contiune up the hill when you find a small boulder covered in moss. Would you like to rest?"))
    if rest_on_boulder.formatted()=='y':
        actions_char=input("What would you like to do. Type in help to show possible commands.")
        if actions_char.formatted()=='help':
            print(possible_commands)
            actions_char=input("What would you like to do. Type in help to show possible commands.")
        elif actions_char.formatted()=='save character':
            methods.save_character(class_instance,file_name=input("File name?"))
            #possible_commands=("save character","check stats","exit","access attribute","create new character","delete character")

        elif actions_char.formatted()=='access attribute':
            methods.access_attribute(attribute_name,class_instance)
        elif actions_char.formatted()=='check stats':
            print(class_instance.__str__())
        elif actions_char.formatted()=='exit':
            raise SystemExit
        elif actions_char.formatted()=='create new character':
            create_character(input2=input("Would you like to create a new character"))
        elif actions_char.formatted()=='delete character':
            pass
            #Deleting function needs updating. TODO: Update del_dict function and move to methods.py
        else:
            raise InvalidInputError
    elif rest_on_boulder.formatted()=='n':
        print("You avoid the rock and continue up the hill.")
        print("You see a sign that says Manchester ->. You follow the sign. Not knowing what fate will approach you.")
        print("You cant believe your eyes. You come accross the Ethiad Stadium. You see thousands of blue and red jerseys where the red team appears to be losing.")
        print("You come accross Kyle Walker.")
        kyle_walker=input("Would you like to fight him? (joke)")
        if kyle_walker.formatted()=='y':
            pass
            kyle_walker_dodge=random.randint(0,100)
            if kyle_walker_dodge<=20:
                print("Oh no. Kyle Walker has dodged the attack.")
            else:
                if input("Do you choose to attack or flee?").formatted()=='attack':
                    class_instance.atttack(methods.Prime_Kyle_Walker)
                    Prime_Kyle_Walker.take_damage1()
                elif input("Do you choose to attack or flee?").formatted()=='flee':
                    flee_attempt(methods.flee_probabilities,methods.Prime_Kyle_Walker)

            if methods.Prime_Kyle_Walker.health<=0:
                pass
                print("You won the battle")
            elif class_instance.health<=0:
                print("You lost the battle")
                lives-=1
                if lives==0:
                    print("Sorry, you lost the game. you suck")
                    print(save_character(class_instance,file_name=input("Enter file name?")))
                    
        elif kyle_walker.formatted()=='n':
            flee_attempt(methods.flee_probabilities,methods.Prime_Kyle_Walker)
            print(shop_instance)
        


        
        
        else:
            raise InvalidInputError
    
        
        




            
        

        








    
        


        




        #wrong path variable stored
        #path=int(input("Which path would you like to take. 1 or 2."))
        #lives=3
        #if path==wrong_path:
            ##########  
                    

                    


                #else:
                   ##print("Ouch!")


                    
                

            


        

    

        
    

    


    
        

        
