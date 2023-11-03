#!/usr/bin/env python
#
#  _                    _             _  
# | |    __ _ _ __ ___ | |__       _-(")-
# | |   / _` | '_ ` _ \| '_ \    `%%%%%  
# | |__| (_| | | | |_| | |_) | _  // \\  
# |_____\__,_|_| |_| |_|_.__/_| |__  ___ 
#                  | |   / _` | '_ \/ __|
#                  | |__| (_| | |_) \__ \
#  2023-07-30      |_____\__,_|_.__/|___/
#
#-------------------------------------
# Title:        TerminalDisplayImage
# Version:      1.0
# Release Date: 2023-07-30
# Author:       Krzysztof Wegner (Owieczka)
#-------------------------------------

import argparse
import sys
import os
#import threading
#import queue

import numpy as np
import imageio
import shutil
import cv2

#--------------------------------------
# Screen Class
#--------------------------------------
class Screen:
  @classmethod
  def init_tty(cls) -> None:
    if sys.platform.startswith("linux"):
      import tty, termios
      cls.org_termios = termios.tcgetattr(0)
      tty.setraw(0)
    elif sys.platform.startswith("win32"):
      pass
    else:
      raise Exception(f"Not supported platform: {sys.platfrom}")

  @classmethod
  def deinit_tty(cls) -> None:
    if sys.platform.startswith("linux"):
      import termios
      termios.tcsetattr(0,termios.TCSANOW, cls.org_termios)
    elif sys.platform.startswith("win32"):
      pass

  @staticmethod
  def wr(s : str | bytes) -> None:
    if isinstance(s, str):
      s = bytes(s, "utf-8")
    os.write(1,s)

  #@staticmethod
  #@overload
  #def wr(s : bytes) -> None:
  #  os.write(1,s)

  @staticmethod
  def cls() -> None:
    Screen.wr(b"\x1b[2J") # ESC [2J

  @staticmethod
  def reset_formats() -> None:
    Screen.wr(b"\x1b[0m")

  @staticmethod
  def save_cursor_position() -> None:
    Screen.wr(b"\x1b\x1b7") # ESC ESC 7

  @staticmethod
  def restore_cursor_position() -> None:
    Screen.wr(b"\x1b\x1b8") # ESC ESC 8

  @staticmethod
  def cursor(show: bool) -> None:
    if show:
      Screen.wr(b"\x1b[?25h") #ESC [?25h
    else:
      Screen.wr(b"\x1b[?25l") # ESC [?25l

  @staticmethod
  def goto(x: int, y: int) -> None:
    Screen.wr(f"\x1b[{y+1};{x+1}H") # ESC

  @staticmethod
  def screen_size() -> tuple[int, int]:
    return shutil.get_terminal_size()

#--------------------------------------
# Keyboard Class
#--------------------------------------
class Keyboard:
  if sys.platform.startswith("linux"):
    kbuf = b""
    @classmethod
    def get_input(cls):
      if cls.kbuf:
        key = cls.kbuf[0:1]
        cls.kbuf = cls.kbuf[1:]
      else:
        key = os.read(0,32)
        if key[0]!= 0x1b:
          key = key.decode()
          cls.kbuf = key[1:].encode()
          key = key[0:1].encode()
      return key
  elif sys.platform.startswith("win32"):
    @classmethod
    def get_input(cls):
      from msvcrt import getch
      return getch()

#--------------------------------------


if sys.platform.startswith("linux"):
  #PIXEL_CHARACTER = u'\u2580'
  PIXEL_CHARACTER = bytes(u'\u2580',"utf-8")
elif sys.platform.startswith("win32"):
  PIXEL_CHARACTER = b'\xdf'

def display(img_src):
  src_height, src_width, src_ch = img_src.shape
  display = b""
  
  for y in range(src_height//2):
    for x in range(src_width):
      #display += f"\x1b[38;2;{img_src[y*2+0,x,0]};{img_src[y*2+0,x,1]};{img_src[y*2+0,x,2]}m"
      #display += f"\x1b[48;2;{img_src[y*2+1,x,0]};{img_src[y*2+1,x,1]};{img_src[y*2+1,x,2]}m"
      display += bytes(f"\x1b[38;2;{img_src[y*2+0,x,0]};{img_src[y*2+0,x,1]};{img_src[y*2+0,x,2]}m","utf-8")
      display += bytes(f"\x1b[48;2;{img_src[y*2+1,x,0]};{img_src[y*2+1,x,1]};{img_src[y*2+1,x,2]}m","utf-8")
      #display += "\xe2\x96\x80"
      #display += u'\u04d2'
      #display += u'\ue29680'
      #display += u'\u2580'
      display += PIXEL_CHARACTER
    display += b"\x1b[38;2;0;0;0m"
    display += b"\x1b[48;2;0;0;0m"
    #display += b"\r\n"
    Screen.wr(display) # Hack for Windows 
    display = b"\r\n"
  
  #Screen.wr(display[:-2]) # Optimal for Linux
  
  #Screen.wr("\r\n")
  #Screen.wr(display)
  
def resize_image(src_img, dst_width, dst_height):
  #src_height, src_width, _ = img.shape
  
  dst_img = cv2.resize(src_img, dsize=(dst_width, dst_height), interpolation=cv2.INTER_AREA)
  
  return dst_img

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("filename")
  parser.add_argument("-sx",default=0,type=int)
  parser.add_argument("-sy",default=0,type=int)
  parser.add_argument("-dx",default=32000,type=int)
  parser.add_argument("-dy",default=32000,type=int)
  parser.add_argument("--interactive", action='store_true')
  args = parser.parse_args()
  filename = args.filename
  sx = args.sx
  sy = args.sy
  dx = args.dx
  dy = args.dy

  app_is_running = args.interactive
  
  Screen.init_tty()
  Screen.cursor(False)
  
  columns, rows = Screen.screen_size()
  #Screen.wr(f"Screen size: {columns}x{rows}\r\n")
  if not args.interactive:
    rows = rows-1
  rows = rows*2

  #Screen.wr(f"{filename}\r\n")

  image_src = imageio.v3.imread(filename)

  image_height, image_width, _ = image_src.shape
  dx = min(dx, image_width)
  dy = min(dy, image_height)
  ex = min(sx+dx,image_width)
  ey = min(sy+dy,image_height)

  if not args.interactive:
    Screen.wr(f"Image size: {image_width}x{image_height}\r\n")

  Screen.cls()
  Screen.goto(0,0)
  Screen.save_cursor_position()

  while True:
    image_croped = image_src[sy:ey,sx:ex,:]

    image_height, image_width, _ = image_croped.shape

    #Screen.wr(f"Crop {sx}x{sy}-{ex}x{ey} {dx}x{dy}\r\n")
    #Screen.wr(f"Image crop: {image_width}x{image_height}\r\n")

    image_dst_width_a = int(rows * image_width / image_height)
    image_dst_height_a = rows

    image_dst_width_b = columns
    image_dst_height_b = int(columns * image_height / image_width)


    image_dst_width = image_dst_width_b
    image_dst_height = image_dst_height_b

    if image_dst_width_a<columns:
      image_dst_width = image_dst_width_a
      image_dst_height = image_dst_height_a    

    image_dst = resize_image(image_croped, image_dst_width, image_dst_height)

    #Screen.wr(f"{image_width}x{image_height}\r\n")
    #Screen.wr(f"{image_dst_width_a}x{image_dst_height_a} {image_dst_width_b}x{image_dst_height_b}\r\n")
    #Screen.wr(f"{image_dst_width}x{image_dst_height}\r\n")
    Screen.restore_cursor_position()
    display(image_dst)
    if args.interactive:
      key = Keyboard.get_input()
     
      #character = keyboard_queue.get(1)
      match key:
        case b"a":
          sx = sx - 1
          ex = ex - 1
        case b"d":
          sx = sx + 1
          ex = ex + 1
        case b"w":
          sy = sy - 1
          ey = ey - 1
        case b"s":
          sy = sy + 1
          ey = ey + 1
        case b"=": # Plus + Zoom in
          dx = dx // 2
          dy = dy // 2
          dx2 = dx // 2
          dy2 = dy // 2
          cx = (ex + sx) // 2
          cy = (ey + sy) // 2
          sx = cx - dx2
          ex = cx + dx2
          sy = cy - dy2
          ey = cy + dy2           
        case b"-": # Minus - Zoom out
          dx = dx * 2
          dy = dy * 2
          dx2 = dx // 2
          dy2 = dy // 2
          cx = (ex + sx) // 2
          cy = (ey + sy) // 2
          sx = cx - dx2
          ex = cx + dx2
          sy = cy - dy2
          ey = cy + dy2
        case b"q":
          app_is_running = False
    #print(f"{image_src.shape}")
    #Screen.wr(key)
    if not app_is_running:
      break
  
  Screen.cursor(True)
  Screen.reset_formats()
  Screen.deinit_tty()

if __name__=="__main__": 
  main()
