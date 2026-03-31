# Authoring course material

## Layout

The layout of the project is like so; 

```bash
course/
    - _quarto-X.yml # These are configuration files.
    - lessons/ 
        - week_X.qmd # Week plan combining several exercises
        - week_Y.qmd
        - exercises/
            - exercise_name_something.qmd # A specific exercise
            - exercise_name_something_else.qmd    
```

The `week_X.qmd` files include the exercises using a bit of quarto magic making it 
simpler to reorganize them. 

## Markdown 

The exercises are written in quarto's `.qmd` format as this allows regular text and 
code to be expressed in a format that is friendly for version control. 

Regular text can be written in regular Markdown syntax, some common bits are: 

#### Math

For inline math use dollar sign fencing `$x = 1$`, which will look like this: $x = 1$. 

For math on its own line using double sign fencing like this
```
$$ 
y = a x + b
$$
```
Which will render as 
$$ 
y = a x + b
$$


The syntax inside the fencing is basically LaTeX, so very pretty equations can be written.

#### Headers 

Headers are denoted with `#` with a single `#` yielding the largest header and adding more 
decreases the size. 

See the quarto's [Markdown Basics](https://quarto.org/docs/authoring/markdown-basics.html) 
for a more complete guide.

## Code 

In regular markdown a code block can be created like this 

````
```python
print("Hello, world")
```
````
This is however **not** executable code, to also write executable code Quarto extends this 
syntax like so

````
```{python}
print("Hello, executable world.")
```
````
So the difference is just the inclusion of the brackets `{}`. To facilitate having both 
a student and instructor ("master") version of the exercises another Quarto feature is used, tagging cells. 

Here is a cell tagged as a solution that will not be rendered in the student version
````
```{python}
#| solution: true
print("Hello, solution world.")
```
````
To give the students a cell to work in or part of a solution use instead 
````
```{python}
#| exercise: true
#| eval: false
my_string = "Hello, exercise world"
... # Your code here

```
````
When rendered these will be automatically be stripped out of the appropriate versions. 







