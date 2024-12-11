# MinSym

A programming language desinged to be near pain english

## Why?

I initially chose my final project to be a challenge on how expressive I can make a language without the use of symbols, but after writing some examples, I realized symbols were neccassary to make the program readable, so I decided that rather than challenging my self to make a language with no symbols, I would create a language that is alost plain english, then try to make this program as expressive as possible. I wanted to make a program that can be a tool for learning programming and a tool for fairly complex tasks.

## Before Quick Start

You must have both [Python](https://www.python.org/) and [TextX](https://textx.github.io/textX/index.html) installed and configured to your environment

## Quick Start

If you haven't already, download the file from the webpage: [MinSym](https://romelaleman.github.io/minsym/). It will likely be flagged as a virus, you have my word that it is NOT malicious, I just dont know how to make a executable for these types of dependencies.

Unzip the file to any location you want.

Open the file and run the file 'run.bat', if everything is configured correctly, this should print out "Hello, World!" to the console. Agian, it will likely be flagged as a virus, just press 'more info' and press 'run anyway'.

In the file, 'testing.minsym' will be the location of your code (feel free to use any textx editor), you can add and change the names of the minsym file, just remember to update the name in the minsym.py file.

## Feature Overview

### General Purpose Features

Introduction to some of the features and syntax of the language

#### Variables and Printing
```
assign "John" to fn

assign "Doe" to ln

assign 31 to age

print variable fn and " " and variable ln and "'s is " and variable age
```
```
John Doe age: 31
```
#### Loops, conditionals, and iterate

```
assign 1 to i
assign 5 to j

while variable i is less than or equal to variable j
    print variable i
    iterate variable i by 2
end while

for i from 1 to variable j
    print variable i
end for
```
```
1
3
5

1
2
3
4
5
```
#### Lists

```
assign list containing () to numbers

assign 1 to i

while variable i is less than or equal to 10
    add (variable i) to list numbers
    iterate variable i by 1
end while

print variable numbers

assign 100 to item 9 in list numbers 

print ""

print variable numbers
```
```
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

[1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
```

#### Functions

```
function addition returns number with a, b
    return variable a plus variable b
end function

assign function addition with 2, 2 to result

print variable result
```
```
4
```

#### Classes and inheritence

```
define person as name, age
    function can_rent_car returns boolean with nothing
        if attribute age is greater than or equal to 25 then
            return true
        else then
            return false
        end if
    end function
end define

define athlete which inherits from person as sport
end define

John is athlete as "John Doe", 31, "Soccer"

print John function can_rent_car with nothing

print John attribute name and "'s age is " and John attribute age and " and plays " and John attribute sport
```
```
True
John Doe's age is 31 and plays Soccer
```

## In Progress Features

A list of features I want to add in the future

#### Better distributable

I need to make it so that it isn't flagged as a trojan by Windows Defender.

#### Optional arguments for functions

At the moment, you can't not give arguments to functions when calling. A way to get around this is just passing 'nothing' without the apostraphes.

```
function print age returns boolean with nothing
    return attribute age
end function

print function age
```

#### More array functions

Unsure on how to make the syntax, but I want to add multidimensional arrays.

#### Built in data structures

I have an idea on making built in data structures that can be made with some required arguments as well as built in functions for the data structure such as adding, deleting, sorting, etc.

#### General flexibility

Given the timing of the project, I couldn't make the program as flexable with what you can do with the tools of the language. Small things like giving operations or comparisons as an argument instead of just a primitive type or variable.

#### Class privacy and access features

#### Better error handling

I couldn't figure out how to capture textx exceptions and return the location of what's causing the error in the source file