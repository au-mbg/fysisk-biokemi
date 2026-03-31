# Git 

## Basic workflow 

The basic workflow involves only a few commands. As an example consider having updated 
an exercise file such as `course/lessons/exercises/inter-bindin-data.qmd`. 
It's always a good idea to check what the current status of the repository is, like so

```bash
git status
```

Which would output something like this

```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   course/lessons/exercises/inter-bindin-data.qmd

no changes added to commit (use "git add" and/or "git commit -a")
```

To add the changes we then use

```bash
git add course/lessons/exercises/inter-bindin-data.qmd
```
After which another call to `git status` would have changed the status of that file. 
To then commit the changes call
```
git commit -m "Updated exercise with new material on X and Y."
```
Assuming we're happy with the changes at this point the changes can then be pushed 
to the remote 
```bash
git push
```
If there are no conflicting commits on the remote then this is all good and the CI 
will automatically build the new material including the website, PDF's and the notebooks.

### Conflicts

If there is a merge conflict this call will throw an error and ask us to merge the 
remote before pushing
```bash
git pull
```

This might output something like:
```
Auto-merging course/lessons/exercises/inter-bindin-data.qmd
CONFLICT (content): Merge conflict in course/lessons/exercises/inter-bindin-data.qmd
Automatic merge failed; fix conflicts and then commit the result.
```

Then use `git status` again to see what file has a conflict:
```bash
git status
```

Which would show:
```
On branch main
Your branch and 'origin/main' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" to merge the remote branch into yours)

You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   course/lessons/exercises/inter-bindin-data.qmd

no changes added to commit (use "git add" and/or "git commit -a")
```

Opening `course/lessons/exercises/inter-bindin-data.qmd` would show conflict markers like:
```
---
title: "Inter-molecular Binding Data"
format: html
---

# Introduction

<<<<<<< HEAD
This exercise focuses on analyzing protein-ligand binding data using 
fluorescence spectroscopy. We'll examine binding curves and calculate 
dissociation constants.
=======
This exercise explores protein-ligand interactions through binding assays.
We will analyze binding isotherms and determine equilibrium constants.
 >>>>>>> origin/main
```

The section between `<<<<<<< HEAD` and `=======` shows your local changes, while the section between `=======` and `>>>>>>> origin/main` shows the incoming changes from the remote repository.

To resolve the conflict:
1. Edit the file to choose which version to keep or combine both
2. Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Save the file

For example, you might resolve it as:
```
This exercise focuses on analyzing protein-ligand binding data using 
fluorescence spectroscopy and binding assays. We'll examine binding curves 
and calculate dissociation constants and equilibrium constants.
```

Many editors will have buttons to choose what to accept - local changes, 
incoming changes or both.

Then add, commit and push like normal:
```bash
git add course/lessons/exercises/inter-bindin-data.qmd
git commit -m "Resolved merge conflict in binding data exercise"
git push
```

One of the key advantages of using Quarto `.qmd` files over Jupyter `.ipynb` notebooks for educational content is their git-friendliness. Jupyter notebooks are stored as JSON files containing not just the code and Markdown, but also execution metadata, output data, and cell execution counts. This means that even running a notebook without changing any actual content will modify the file and create meaningless git diffs. In contrast, `.qmd` files are plain text Markdown with embedded code blocks, making them much cleaner for version control. Git diffs show exactly what content changed rather than being cluttered with metadata updates. Additionally, merge conflicts in `.qmd` files are human-readable and easier to resolve, whereas notebook merge conflicts often involve complex JSON structures that are somewhere between difficult and impossible to parse manually.

## Build using Github Actions (CI)

### What is CI?

CI stands for "Continuous Integration" - an automated system that runs whenever changes are pushed to GitHub. It functions as a helpful robot that automatically builds course materials every time updates are made. Instead of manually running commands like `make website` on a local computer, the CI system handles this process in the cloud.

### How Our CI Works

When commits are pushed to the repository, GitHub automatically:

1. **Detects the changes** - GitHub notices new commits have been pushed
2. **Starts a virtual computer** - GitHub spins up a clean Linux machine in the cloud
3. **Downloads the code** - The virtual machine gets the latest version of the repository
4. **Installs dependencies** - Sets up Python, Quarto, and all required packages
5. **Builds the content** - Runs the build commands to create both student and master versions
6. **Deploys the website** - Publishes the updated course website automatically

### What Gets Built Automatically

Every push triggers the CI system to build:

- **Student website** - The version with exercises only (solutions stripped out)
- **Master website** - The version with both exercises and solutions  
- **PDF versions** - Downloadable PDF files of the course materials
- **Jupyter notebooks** - `.ipynb` files that work with Google Colab
- **Datasets** - Aggregates the datasets and makes them downloadable.

### Checking Build Status

After pushing changes, build status can be checked by:

1. Going to the repository frontpage [https://github.com/au-mbg/fysisk-biokemi](https://github.com/au-mbg/fysisk-biokemi)
2. Clicking the **Actions** tab at the top
3. Viewing the list of recent builds with status indicators:
   - ✅ Green checkmark = Build succeeded
   - ❌ Red X = Build failed
   - 🟡 Yellow dot = Build in progress

### What to Do If Builds Fail

When a red X (failed build) appears:

1. Click on the failed build to see details
2. Look for error messages in the build logs
3. Common issues include:
   - **Syntax errors** in `.qmd` files
   - **Missing files** referenced in content
   - **Broken Python code** in code blocks
   - **Invalid YAML** in frontmatter

Fixing the issue in local files, then committing and pushing again will trigger an automatic retry.

### Benefits of Automated Building

- **No manual work** - Content creation and pushing is all that's required; everything else happens automatically
- **Consistent builds** - The same process runs every time, reducing errors
- **Multiple outputs** - Student and master versions are always kept in sync
- **Always up-to-date** - The website reflects the latest changes within minutes
- **Collaboration-friendly** - Multiple people can contribute without build conflicts

The CI system enables focusing on creating great educational content without worrying about the technical details of building and deploying the course materials.
