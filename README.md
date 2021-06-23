# pico-stuff
A place to dump all my Raspberry Pi Pico code

## Pong
The famous pong game written in MicroPython. Requires a [Pimoroni Display Pack](https://shop.pimoroni.com/products/pico-display-pack).

## Pong Multithread
An attempt at a multithreaded version of Pong. It runs smoothly but there's either a memory leak or an inter-core FIFO overload which causes the Pico to crash after running for about a minute. Code is a mess as I was trying to find the cause of the crash.

## Rotation
Implemented a basic sprite class that can be rotated to any angle. Can currently only draw a rectangle and it's pretty slow but uses frametime calculation (delta) to decouple rotation and translation from the framerate.
