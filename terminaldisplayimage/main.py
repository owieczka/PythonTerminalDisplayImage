#!/usr/bin/env python
import argparse
import numpy as np
import imageio
import shutil
import cv2

def display(img_src):
  src_height, src_width, src_ch = img_src.shape
  display = ""
  
  for y in range(src_height//2):
    for x in range(src_width):
      display += f"\x1b[38;2;{img_src[y*2+0,x,0]};{img_src[y*2+0,x,1]};{img_src[y*2+0,x,2]}m"
      display += f"\x1b[48;2;{img_src[y*2+1,x,0]};{img_src[y*2+1,x,1]};{img_src[y*2+1,x,2]}m"
      #display += "\xe2\x96\x80"
      #display += u'\u04d2'
      #display += u'\ue29680'
      display += u'\u2580'
    display += f"\x1b[38;2;0;0;0m"
    display += f"\x1b[48;2;0;0;0m"
    display += "\n"
  
  print(display[:-1])
  
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
  args = parser.parse_args()
  filename = args.filename
  sx = args.sx
  sy = args.sy
  dx = args.dx
  dy = args.dy
  print(f"{filename}")

  image_src = imageio.v3.imread(filename)
  #image_src = image_src[1600:1700,1600:1700,:]

  columns, rows = shutil.get_terminal_size()
  rows = rows-1
  rows = rows*2

  print(f"Screen size: {columns}x{rows}")

  image_height, image_width, _ = image_src.shape

  print(f"Image size: {image_width}x{image_height}")

  ex = min(sx+dx,image_width)
  ey = min(sy+dy,image_height)

  image_src = image_src[sy:ey,sx:ex,:]

  image_height, image_width, _ = image_src.shape

  print(f"Crop {sx}x{sy}-{ex}x{ey} {dx}x{dy}")
  print(f"Image crop: {image_width}x{image_height}")

  image_dst_width_a = int(rows * image_width / image_height)
  image_dst_height_a = rows

  image_dst_width_b = columns
  image_dst_height_b = int(columns * image_height / image_width)


  image_dst_width = image_dst_width_b
  image_dst_height = image_dst_height_b

  if image_dst_width_a<columns:
    image_dst_width = image_dst_width_a
    image_dst_height = image_dst_height_a    

  image_dst = resize_image(image_src, image_dst_width, image_dst_height)

  print(f"{image_width}x{image_height}")
  print(f"{image_dst_width_a}x{image_dst_height_a} {image_dst_width_b}x{image_dst_height_b}")
  print(f"{image_dst_width}x{image_dst_height}")
  display(image_dst)  
  
  #print(f"{image_src.shape}")

if __name__=="__main__": 
  main()
