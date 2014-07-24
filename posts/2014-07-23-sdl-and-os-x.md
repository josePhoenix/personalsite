---
title: "SDL 2.0 and Xcode 5.1: Part I"
excerpt: "Setting up Xcode 5.1 for development with SDL 2.0, then getting a test program to compile and run"
---

Many, many moons ago (when I was a wee middle-schooler), SDL was the easy way to do anything with graphics cross-platform. Perhaps that's an exaggeration, but as a nerdy child trying to show things developed on Linux to (slightly less) nerdy children that used Windows, I ended up using SDL.

Recently, after not hearing anything about SDL for a while, SDL 2.0 was released to great fanfare. I thought it was time to give it another try, since I've safely forgotten everything I knew about the previous version.

I'm also using a Mac now, so that's what we'll be using for this guide.

# Step 0: Before you even get started

You will need a Mac running the latest versions of OS X and Xcode. Xcode is a [free download from the App Store](https://itunes.apple.com/us/app/xcode/id497799835?mt=12), but you probably already knew that.

You will also need the latest compiled version of SDL 2 for Mac OS X. You can get it [here](http://libsdl.org/download-2.0.php) (scroll down to "Development Libraries").

# Step 1: Install the framework

Open the disk image you downloaded. Copy the `SDL2.framework` bundle to `/Users/yourusername/Library/Frameworks` for development purposes. For me, it's easiest to use the Terminal. (Note: you can drag and drop the framework bundle onto the Terminal window to fill in its path for the `cp` command.)

```bash
mkdir -p ~/Library/Frameworks
cp -R /Volumes/SDL2/SDL2.framework ~/Library/Frameworks/
```

**Note:** I ran into a problem with the compiled Mac version of SDL that crashed Xcode due to a code signature mismatch. The [simple fix](http://stackoverflow.com/questions/22368202/xcode-5-crashes-when-running-an-app-with-sdl-2) is to update the signature right after you install it.

```bash
codesign -f -s - ~/Library/Frameworks/SDL2.framework/SDL2
```



# Step 2: Make an Xcode project

Open Xcode and create a new Cocoa project. We aren't building a Cocoa app, so we'll have to remove some Cocoa-specific files in the project structure Xcode makes for us.

![Create a new Cocoa project using the Xcode wizard](new_cocoa_project.png)

Just fill in a name for the project; everything else should be left the same. (You could also change your developer identifier, if you wanted to.)

![Naming the Xcode project](new_project_details.png)

You'll have to choose a place to save the project, then you'll see the project view in the main Xcode window. Before we remove the Cocoa-specific files, we should add a `main.c` file. It's not actually important that it's called `main.c`, but it *does* need to be added to your app target using the panel at the bottom of the save dialog. Save it in the same directory as `main.m`, which we'll remove in the next step.

![Making a main.c file](saving_main_file.png)

# Step 3: Pruning superfluous files and frameworks

Now it's time to remove some extra files we don't need. Here's what my project looks like just after adding `main.c`, but before removing files and framework references. Select the files as shown, then right- or control-click them and choose "Delete", then "Move to Trash" in the following dialog.

![The project sidebar before removing unneeded files](files_to_delete.png)

Next, remove references to frameworks we will not be using. Select them as shown in the image below, right- or control-click them and choose "Delete", then "Remove References" in the following dialog.

![Frameworks to remove references to](frameworks_to_remove.png)

The final step of pruning is to tell Xcode not to expect a precompiled header file for our project. Select the project name at the top of the sidebar, then "Build Settings" in the main pane. Set "Precompile Prefix Header" to "No" as shown. Clear the path in the "Prefix Header" setting, leaving that setting empty.

![Disable "Precompile Prefix Header"](disable_pch.png)

The last thing to do is to remove the test target, since we're not using the Xcode testing framework. Expand the project targets drawer...

![Expand the targets drawer](expand_targets_drawer.png)

then select the test target and click the "-" button. When prompted, confirm you really want to delete this target.

![Remove the test target](remove_test_target.png)

(Wasn't all that just excruciating? Maybe it's just because I'm used to Makefiles and doing everything from the Terminal, but it seems way more complicated than it should be to make a non-Cocoa app. Which is, I guess, exactly what Apple wants.)

# Step 4: Add the SDL framework

For our test app to compile, we need to add the SDL framework bundle.

![Click the + icon to add the SDL Framework](add_framework.png)

Since I installed my copy of the framework under my home folder, I had to choose "Add Other...". Use Command-Shift-G to open the "Go to folder" sheet, and type in `~/Library/Frameworks/`. Then you'll see `SDL2.framework`. Add it.

## Step 4.1: Package the framework in your app

If you don't package the framework with your app, people will have to install SDL to use it. This tends to annoy people, so you should copy it into the app bundle automatically. Select the project from the left sidebar, then choose "Build Phases" for your app target. Click the "+" button under "Copy Bundle Resources", then choose `SDL2.framework` to add.

![The button to add bundle resources to copy](copy_resources.png)

# Step 5: Actually fill in `main.c`

We just want to make sure we're successfully linking against SDL2, and make sure SDL can initialize successfully, so we'll use the world's simplest quick-and-dirty test program.

```c
#include <SDL2/SDL.h>

int main(int argc, const char * argv[]){
    if(SDL_Init(SDL_INIT_EVERYTHING) != 0)
    {
        puts("SDL_Init error");
        return -1;
    } else {
        puts("SDL_Init success!");
        return 0;
    }
}
```

Now, the moment we've all been waiting for... compile and run with Command-R! If everything worked, you'll see `SDL_Init success!` output in the lower pane of Xcode.

![Successful output in Xcode](success.png)

Next time we'll draw some actual pictures.