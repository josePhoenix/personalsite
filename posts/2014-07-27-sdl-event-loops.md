---
title: The SDL Event Loop
excerpt: "Making an SDL app that actually does something a little more interesting than last time"
draft: true
---

Last time we successfully built and packaged a minimal program that built on SDL. However, it didn't do anything interesting except ensure SDL was able to initialize without errors. It didn't even open a window. How primitive!

Well, it turns out opening a window requires explaining a few things, and I didn't want to put too much in one post. Also, from this point onwards, our use of SDL means this code won't be OS X specific. Certain features might be OS X specific (like setting a dock icon), and building on other platforms is up to you to figure out, but the code will generally be unchanged for other platforms.

# One window, please!

Every operating system has their own conventions for creating graphics windows and drawing things in them. My main use for SDL is to wrap around these OS-specific APIs and provide a consistent way to draw things. It's still pretty low level, giving you a lot of control over the resulting application.

So, how do we ask for a window? 

```c
#include <SDL2/SDL.h>

#define WINDOW_WIDTH 640
#define WINDOW_HEIGHT 480


int main(int argc, char* argv[])
{
    if(SDL_Init(SDL_INIT_EVERYTHING) != 0)
    {
      puts("SDL_Init error");
      return -1;
    };

    SDL_Window* window = SDL_CreateWindow(
      "SDL Example: Event Loop",
      SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, // x position, y position
      WINDOW_WIDTH, WINDOW_HEIGHT,
      0); // bitwise flags for special window features
    
    if (!window)
    {
      puts("SDL couldn't create the window");
      return 1;
    }

    SDL_Delay(5000); // milliseconds
    
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
```

Build it and run! A black window appears, hangs around for five seconds, then is removed and the program exits.

This starts just out like our test program, but we have introduced a few more `SDL_`-prefixed functions. `SDL_CreateWindow` does the heavy lifting, accepting arguments for title, position, size, and special flags. It returns an ID for the window in the form of an `SDL_Window` pointer, or zero if it failed.

`SDL_Delay` should be easy to figure out from context. The argument is how long to delay in milliseconds.

`SDL_DestroyWindow`, the counterpart to `SDL_CreateWindow`, similarly does the OS-specific tasks to remove the window.

`SDL_Quit`, well, quits.

# The Spinning Pinwheel of Death


<div style="text-align: center; font-style: italic">
  <img src="spod.gif" alt="The Mac OS X busy cursor">
  Waiting, and waiting, and waiting...
</div>

Our program compiles fine, but you may notice that before it exits you get the so-called "spinning pinwheel of death", the cursor that indicates your computer is busy and the application is not responding. This usually presages some unfortunate event, like a crash. Why is our program doing this?

To answer this, we have to talk about the central concept in GUI programming: the event loop.

# The Event Loop

Try running a command in the Terminal. Say, `ls`.

```
# ls
Info.plist  Makefile    build       main        main.c
#
```

Did you see that? `ls` ran, then exited as soon as it had listed your files. Programs written in the early days of UNIX were, with some exceptions, of this kind. They run only long enough to produce some output, then return to your shell.

The expectations are different for GUI programs! They have to wait on you to interact with them through mouse and keyboard events, and they won't quit unless you ask them to. Not only that, they have to ask the operating system for your input events *regularly*, or the OS assumes they've crashed. (Hence the spinning pinwheel of death.)

So, let's add one to our program. An event loop is *very like* an infinite loop. You're not iterating over some data structure, and you're not waiting for any condition within your program like reaching some minimum error on an approximation. You're waiting for the user to be done with you.

Put the following where the call to `SDL_Delay` was, removing the delay:

```c
    int will_quit = 0; // how we know to break out of our "infinite" loop
    SDL_Event event; // the event we'll get
    while (!will_quit) {
        SDL_PollEvent(&event);
        if (event.type == SDL_QUIT)
        {
            will_quit = 1; // bail next time we test the loop condition
        }
    }
```

If you tried to click the close button on the window previously, you probably noticed that nothing happened. Here, when you build the new and improved code, you can quit the program just by clicking the window's close button. The operating system tells SDL about your click, and SDL passes this on to you for handling as you wish (e.g. ending the event loop, or prompting "Are you sure?").

Run this code and open the Activity Monitor or Task Manager. See anything weird?

Our do-nothing program is using up 100% of the available CPU! That's why tight infinite loops are bad, you know. Let's make it a little more friendly by adding `SDL_Delay(50);` on a new line just before the call to `SDL_PollEvent`. (If we were making a game, we'd want to do something more sophisticated, like measure the time per iteration of the loop and use that to cap the frame rate. But we're not, so let's keep it simple.)

Our program still doesn't do much, but now that we have an event loop in place we have all the "plumbing" necessary to react to the user. We're also well behaved citizens of the user's computer, quitting when asked and not using more CPU than we need.

# Really, how much more preamble could there be?

You'd be surprised. A window is not enough to actually draw things with SDL. (Presumably, you want to draw fancy things, or else you'd be over there in XCode using Interface Builder and playing drag-and-drop.) We also need a renderer, a sort of handle into the SDL drawing machinery.