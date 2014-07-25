---
title: App Bundles with a Makefile
excerpt: "It's no secret Xcode prefers building Cocoa apps to SDL. In this post, I build my SDL test app bundle using a Makefile instead of an IDE."
---

After my [recent Xcode learning experience](/writing/sdl-and-os-x/), I thought I would see if I could accomplish the same things without it. It turns out that it's pretty straightforward to use a plain old `Makefile` to create a nice double-clickable `.app` bundle.

Makefiles are almost as old as Mac OS X's UNIX underpinnings themselves, and pretty simple to use. The command line `make` tool checks the nearest Makefile for instructions, and then, well, makes the build happen.

In it's simplest form, you don't need any Makefile at all. If you have a file called `foo.c`, typing `make foo` in the same directory will produce a binary called `foo` by compiling `foo.c` using your system's C compiler (e.g. the one installed with Xcode). More sophisticated things, like creating a `.app` bundle, can be done by adding some variables and targets to the Makefile.

Similar to [last time](/writing/sdl-and-os-x/), I have made a folder for this project. `SDL2.framework` is installed in my home directory under `~/Library/Frameworks/`, and Xcode and OS X are up to date.

# Step 1: Create our main.c

We'll use the same code as last time, at least to start. Save this as `main.c` (or whatever you like, but remember to change later directions accordingly).

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

# What's in an .app?

<p style="text-align: center; font-style: italic">
That which we call a program, by any other name would smell as sweet...
</p>

App bundles are a clever way of moving executables and their associated resources around while convincing the user that they're one big file. Really, they're just folders with names ending in `.app`, and a few special folders and files that OS X looks for. They are:

  - `Contents/Info.plist` --- Tells Finder and friends what kind of bundle this is and how to use it.
  - `Contents/Resources/` --- Resources needed by the app. Notably, frameworks (a Mac OS X specific way to package libraries) live here
  - `Contents/MacOS/` --- we'll be putting our executable in this folder

We know where to find the SDL2 framework, and we will build our binary shortly, but what about `Info.plist`? We'll have to steal one from an existing app and modify it. Right- or Control-click on an existing app (say, TextEdit) and choose "Show Package Contents". Inside the app, you should see an `Info.plist`. Open it in your favorite text editor and have a look. (*What the hell is all that?*, you're probably thinking.)

Fortunately, it turns out that we can remove most of those properties and still have an app bundle that works. Here's the template I came up with based on the minimal app from last time with Xcode:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleExecutable</key>
	<string>APP_NAME</string>
	<key>CFBundleIdentifier</key>
	<string>com.your-name.APP_NAME</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>APP_NAME</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
</dict>
</plist>
```

Fill in `your-name` appropriately, then save this as `Info.plist` in the same directory as your `Makefile`.

# Step 2: Building a Bundle

Before we automate this with a Makefile, it's good practice to make sure you can put it all together in the terminal. After all, make just runs your commands!

I'm calling my application SDLExample2 (original, I know). I'm putting it in a `build` directory just to keep things organized. (This way I can ignore the whole folder with `.gitignore`, no matter what build products I eventually have.)

1.  Make the .app folder and essential subfolders
    
        mkdir -p ./build/SDLExample2.app/Contents/{MacOS,Resources}
    
2.  Compile `main.c` to make an executable for the bundle

        cc -F "$HOME/Library/Frameworks" -framework SDL2 main.c -o main

    As you can probably guess, `-F` specifies a folder with frameworks in it. `-framework` indicates the name of a framework to link with. If you run it in the terminal you should see something like:

        $ ./main
        SDL_Init success!

3.  Copy the resulting binary into place
    
        cp ./main ./build/SDLExample2.app/Contents/MacOS/SDLExample2

4.  Copy the SDL2 framework into `Resources`

        cp -R "$HOME/Library/Frameworks/SDL2.framework" ./build/SDLExample2.app/Contents/Resources/

5.  Copy in the Info.plist file...

        cp Info.plist ./build/SDLExample2.app/Contents/

    ...and edit it with your favorite text editor. It should look like this, unless you've named the app something other than `SDLExample2`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleExecutable</key>
	<string>SDLExample2</string>
	<key>CFBundleIdentifier</key>
	<string>com.joseph-long.SDLExample2</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>SDLExample2</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
</dict>
</plist>
```

Now you should have an app! An app that doesn't do much! Double click the SDLExample2 icon in the `build` folder and see. If you don't get any error messages about corrupted or incomplete applications, you're good to go.

# Step 3: Make the computer build you a bundle

I was afraid of make and Makefiles for a long time, but I eventually figured out that my fear was from seeing Makefiles made to do things they really ought not to do. It's not a very good language in which to write scripts!

For simple tasks, however, they are more than adequate. Here is my Makefile to automate everything we did in Step 2.

```makefile
FRAMEWORK_PATH=$(HOME)/Library/Frameworks
APP_NAME=SDLExample2
CFLAGS=-F $(FRAMEWORK_PATH) -framework SDL2

all: main clean_app package_app

clean_app:
	rm -rf "./build/$(APP_NAME).app/"

package_app:
	mkdir -p "./build/$(APP_NAME).app"/Contents/{MacOS,Resources}
	cp -R "$(FRAMEWORK_PATH)/SDL2.framework" "./build/$(APP_NAME).app/Contents/Resources/"
	cp Info.plist "./build/$(APP_NAME).app/Contents/"
	sed -e "s/APP_NAME/$(APP_NAME)/g" -i "" "./build/$(APP_NAME).app/Contents/Info.plist"
	cp ./main "./build/$(APP_NAME).app/Contents/MacOS/$(APP_NAME)"
```

The Makefile begins with some variable definitions of the form `FOO=bar`. Including the value of one variable in another is done with the `$(FOO)` construct. (We don't quote variables defined in Makefiles, as the quotes are interpreted literally.) `CFLAGS` is important, since it sets up extra arguments to be passed to the C compiler (like the ones in step 2.2).

The `all` target is special, as it is built (or run) when `make` is invoked without target names. Here we tell it to "build `main`, remove any existing app bundle, and build the app bundle again from scratch".

The `clean_app` target just removes the entire bundle folder.

The `package_app` target is basically the commands we did, one by one, in Step 2. The only thing different here is the use of `sed`'s in-place-editing mode (`-i ""`) to replace `APP_NAME` with our app name defined in the beginning of the Makefile.

Also, note that we have quotes around arguments that include `$(APP_NAME)`. This is so you won't confuse the shell if you set `APP_NAME` to something with spaces in it (e.g. `APP_NAME=SDL Example 2`).

# Making `make` make

Remove the `main` binary and app bundle, if they exist, then run `make` with no arguments. You should see something like this:

```bash
# make
cc -F /Users/josephoenix/Library/Frameworks -framework SDL2    main.c   -o main
rm -rf "./build/SDLExample2.app/"
mkdir -p "./build/SDLExample2.app"/Contents/{MacOS,Resources}
cp -R "/Users/josephoenix/Library/Frameworks/SDL2.framework" "./build/SDLExample2.app/Contents/Resources/"
cp Info.plist "./build/SDLExample2.app/Contents/"
sed -e "s/APP_NAME/SDLExample2/g" -i "" "./build/SDLExample2.app/Contents/Info.plist"
cp ./main "./build/SDLExample2.app/Contents/MacOS/SDLExample2"
```

Look in the `./build/` directory. Do you see an app bundle? 

## *You don't need Xcode to build an app bundle after all!*

I know I should check my shell-based privilege here, but this took me all of one flight to figure out. (It was a short flight too! ATL to BWI.) On the other hand, I futzed around with Xcode for an entire evening to write that other post.
