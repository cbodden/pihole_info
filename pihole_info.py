import subprocess, requests, json, collections, time, sys, os
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
# from font_source_sans_pro import SourceSansPro, SourceSansProBold

## ipadress of the pihole server
pihole_ip = "192.168.100.21"


## initialize the inkyphat and looks
inky_display = InkyPHAT(colour="black")
inky_display.set_border(inky_display.YELLOW)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
color = inky_display.BLACK

## font = ImageFont.truetype(SourceSansPro, 11)
## font_bold = ImageFont.truetype(SourceSansProBold, 11)
font = ImageFont.truetype('fonts/EHSMB.TTF', 9)
font_bold = ImageFont.truetype('fonts/EHSMB.TTF', 10)

max_width = inky_display.HEIGHT
max_height = inky_display.WIDTH
h_line = 12


## 1bit mask canvas to fit the text (rotated 90deg before pasted on 'img' Image)
mask = Image.new("1", (inky_display.HEIGHT, inky_display.WIDTH))


## Set up mask ImageDraw
mask_draw = ImageDraw.Draw(mask)


## Write the text on the mask, using colour 1 (on) as this is an on/off 1bit canvas
#### Stats to display on screen
#### these are pulled into tmp file from info.sh
#### System info
system_title = "SYSTEM INFO "
w_sysinfo, h_sysinfo = font.getsize(system_title)
mask_draw.text(((max_width-w_sysinfo)/2, 0), system_title, 1, font_bold)

host = subprocess.check_output("awk 'NR==1' /tmp/out.file", shell=True, text=True)
w_host, h_host = font.getsize(host)
mask_draw.text((0, h_line*1), "HOST:", 1, font_bold)
mask_draw.text((max_width-w_host+8, h_line*1), host, 1, font)

ip = subprocess.check_output("awk 'NR==2' /tmp/out.file", shell=True, text=True)
w_ip, h_ip = font.getsize(ip)
mask_draw.text((0, h_line*2), "IP:", 1, font_bold)
mask_draw.text((max_width-w_ip+6, h_line*2), ip, 1, font)

mem_usage = subprocess.check_output("awk 'NR==3 {printf \"%s/%sM %.0f%%\", $3,$2,$3*100/$2}' /tmp/out.file", shell=True, text=True)
w_mem, h_mem = font.getsize(mem_usage)
mask_draw.text((0, h_line*3), "MEM:", 1, font_bold)
mask_draw.text((max_width-w_mem, h_line*3), mem_usage, 1, font)

disk = subprocess.check_output("sed -n 4p /tmp/out.file | awk '{printf \"%d/%dG %s\", $3,$2,$5}'", shell=True, text=True)
w_disk, h_disk = font.getsize(disk)
mask_draw.text((0, h_line*4), "DISK:", 1, font_bold)
mask_draw.text((max_width-w_disk, h_line*4), disk, 1, font)

temp = subprocess.check_output("sed -n 5p /tmp/out.file | sed 's/temp=//'", shell=True, text=True)
w_temp, h_temp = font.getsize(temp)
mask_draw.text((0, h_line*5), "TEMP:", 1, font_bold)
mask_draw.text((max_width-w_temp+6, h_line*5), temp, 1, font)
##mask_draw.line([(0, h_line*5+2), (max_width, h_line*5+2)], fill=color, width=2)


## Pi-hole stats
#### this is location on screen for this section
start_h = h_line*7
## start_h = h_line*6+4

rawdata = requests.get("http://" + pihole_ip + "/admin/api.php?summary").json()

stats_title = "PI-HOLE STATS  "
w_title, h_title = font.getsize(stats_title)
mask_draw.text(((max_width-w_title)/2, start_h), stats_title, 1, font_bold)

mask_draw.text((0, start_h+h_line*1), "Clients ", 1, font_bold)

clients_today = rawdata["unique_clients"]
w_clients_today, h_clients_today = font.getsize(clients_today)
mask_draw.text((0, start_h+h_line*2), " Today:", 1, font_bold)
mask_draw.text((max_width-w_clients_today, start_h+h_line*2), clients_today, 1, font)

clients_total = rawdata["clients_ever_seen"]
w_clients_total, h_clients_total = font.getsize(clients_total)
mask_draw.text((0, start_h+h_line*3), " Total:", 1, font_bold)
mask_draw.text((max_width-w_clients_total, start_h+h_line*3), clients_total, 1, font)

dns_queries = rawdata["dns_queries_all_types"]
w_queries, h_queries = font.getsize(dns_queries)
mask_draw.text((0, start_h+h_line*4), "Queries: ", 1, font_bold)
mask_draw.text((max_width-w_queries, start_h+h_line*4), dns_queries, 1, font)

mask_draw.text((0, start_h+h_line*5), "Blocked ", 1, font_bold)

blocked_today = rawdata["ads_blocked_today"]
w_blocked_today, h_blocked_today = font.getsize(blocked_today)
mask_draw.text((0, start_h+h_line*6), " Today:", 1, font_bold)
mask_draw.text((max_width-w_blocked_today, start_h+h_line*6), blocked_today, 1, font)

ads_percentage = rawdata["ads_percentage_today"]
blocked_percent = ads_percentage + " %"
w_blocked_percent, h_blocked_percent = font.getsize(blocked_percent)
mask_draw.text((0, start_h+h_line*7), " Percent:", 1, font_bold)
mask_draw.text((max_width-w_blocked_percent, start_h+h_line*7), blocked_percent, 1, font)

total_blocked = rawdata["domains_being_blocked"]
w_blocked_total, h_blocked_total = font.getsize(total_blocked)
w_tbl, h_tbl = font.getsize("TOTAL BLOCKED  ")
mask_draw.text(((max_width-w_tbl)/2, start_h+h_line*9), "TOTAL BLOCKED", 1, font_bold)
mask_draw.text(((max_width-w_blocked_total)/2, start_h+h_line*10), total_blocked, 1, font)


# Rotate the mask Image so everything is displayed vertically
mask = mask.rotate(90, expand=True)


# Put the mask on the main Image
img.paste(color, (0,0), mask)
draw = ImageDraw.Draw(img)
inky_display.set_image(img)
inky_display.show()
