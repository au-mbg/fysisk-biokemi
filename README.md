# Fysisk biokemi & dataanalyse

## Files and folders
- `course/`: Contains all the files for the exercises and for making the different document types. 
- `course-utils/`: Contains the Python package used for widgets, datasets, and helper utilities.
- `pixi.toml`: Defines the repository environments and tasks used to render the course and build the utility package.
- `.github/workflows/`: Github workflow for making and hosting the static website.

## Using Pixi 

The repository is configured to use `pixi`, this means `pixi` is the only dependency
that needs to be manually installed to interact with the exercises. 

The simplest way is by using the tasks: 

| Task | Description |
| ---- | ----------- |
| preview | Preview the course notes in either student or master mode |
| render | Render the course notes in either student or master mode |
| render-all | Render the course notes in both student and master mode |
| build-wheel | Build the accompanying Python package wheel |

For example, the preview task can be invoked as

```sh
pixi run preview
```

## More

- For authoring or updating exercises see [authoring.md](notes/authoring.md).
- For things related to `git`, including how the website is build and hosted, see [git.md](notes/git.md)


