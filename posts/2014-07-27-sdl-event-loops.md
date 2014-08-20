---
title: The SDL Event Loop
excerpt: "Making an SDL app that actually does something a little more interesting than last time"
---

Last time we successfully built and packaged a minimal program that built on SDL. However, it didn't do anything interesting except ensure SDL was able to initialize without errors. It didn't even open a window. How primitive!

Well, it turns out opening a window requires explaining a few things, and I didn't want to put too much in one post. Also, from this point onwards, our use of SDL means this code won't be OS X specific. Certain features might be OS X specific (like setting a dock icon), and building on other platforms is up to you to figure out, but the code will generally be unchanged for other platforms.

# One window, please!

Every operating system has their own conventions for creating graphics windows and drawing things in them. My main use for SDL is to wrap around these OS-specific APIs and provide a consistent way to draw things. It's still pretty low level, giving you a lot of control over the resulting application.

So, how do we ask for a window? 

```c
#include <SDL2/SDL.h>

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

Did you see that? `ls` ran, then exited as soon as it had listed your files. Programs written in the early days of UNIX were, with few exceptions, 