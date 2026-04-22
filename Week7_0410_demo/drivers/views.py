import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Driver

# 2026 Confirmed Drivers
F1_2026_DRIVERS = [
    {"driverId": "maxver01", "name": "Max Verstappen", "team": "Red Bull Racing", "points": 400,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png"},
    {"driverId": "lewham01", "name": "Lewis Hamilton", "team": "Ferrari", "points": 380,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png"},
    {"driverId": "chalec01", "name": "Charles Leclerc", "team": "Ferrari", "points": 350,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png"},
    {"driverId": "lannor01", "name": "Lando Norris", "team": "McLaren", "points": 330,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png"},
    {"driverId": "oscpia01", "name": "Oscar Piastri", "team": "McLaren", "points": 310,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png"},
    {"driverId": "georus01", "name": "George Russell", "team": "Mercedes", "points": 280,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png"},
    {"driverId": "kimant01", "name": "Kimi Antonelli", "team": "Mercedes", "points": 250,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/K/KIMANT01_Kimi_Antonelli/kimant01.png"},
    {"driverId": "carsai01", "name": "Carlos Sainz", "team": "Williams", "points": 220,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png"},
    {"driverId": "alealb01", "name": "Alexander Albon", "team": "Williams", "points": 210,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png"},
    {"driverId": "feralo01", "name": "Fernando Alonso", "team": "Aston Martin", "points": 200,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png"},
    {"driverId": "lanstr01", "name": "Lance Stroll", "team": "Aston Martin", "points": 180,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png"},
    {"driverId": "piegas01", "name": "Pierre Gasly", "team": "Alpine F1 Team", "points": 150,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png"},
    {"driverId": "jacdoo01", "name": "Jack Doohan", "team": "Alpine F1 Team", "points": 140,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/J/JACDOO01_Jack_Doohan/jacdoo01.png"},
    {"driverId": "estoco01", "name": "Esteban Ocon", "team": "Haas F1 Team", "points": 120,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png"},
    {"driverId": "olibea01", "name": "Oliver Bearman", "team": "Haas F1 Team", "points": 110,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png"},
    {"driverId": "yuktsu01", "name": "Yuki Tsunoda", "team": "RB F1 Team", "points": 100,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png"},
    {"driverId": "isahad01", "name": "Isack Hadjar", "team": "RB F1 Team", "points": 90,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png"},
    {"driverId": "nichul01", "name": "Nico Hulkenberg", "team": "Kick Sauber", "points": 80,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png"},
    {"driverId": "gabbor01", "name": "Gabriel Bortoleto", "team": "Kick Sauber", "points": 70,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png"},
    {"driverId": "lialaw01", "name": "Liam Lawson", "team": "Red Bull Racing", "points": 60,
     "image_url": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png"},
]

# Team color mapping for the gacha card
TEAM_COLORS = {
    'Ferrari': '#E80020',
    'Red Bull Racing': '#3671C6',
    'McLaren': '#FF8700',
    'Mercedes': '#27F4D2',
    'Aston Martin': '#229971',
    'Alpine F1 Team': '#FF87BC',
    'Williams': '#64C4FF',
    'RB F1 Team': '#6692FF',
    'Haas F1 Team': '#B6BABD',
    'Kick Sauber': '#52E252',
}


def home(request):
    """車隊總覽展示牆：依積分高低排序所有已簽約車手"""
    drivers = Driver.objects.filter(is_signed=True).order_by('-points')
    return render(request, 'home.html', {'drivers': drivers})


def recruit(request):
    """抽卡：從尚未簽約的車手池中隨機抽取一位，跳轉至 gacha 揭曉頁"""
    # 找出目前車庫中已存在的 driver_id
    signed_ids = set(Driver.objects.filter(is_signed=True).values_list('driver_id', flat=True))
    # 過濾出可抽卡池
    pool = [d for d in F1_2026_DRIVERS if d['driverId'] not in signed_ids]

    if not pool:
        # 車庫已滿
        return render(request, 'gacha.html', {'pool_empty': True})

    picked = random.choice(pool)
    # 先以 is_signed=False 暫存到 DB，等玩家決定
    driver, _ = Driver.objects.update_or_create(
        driver_id=picked['driverId'],
        defaults={
            'name': picked['name'],
            'team': picked['team'],
            'points': picked['points'],
            'image_url': picked['image_url'],
            'is_signed': False,
        }
    )

    team_color = TEAM_COLORS.get(picked['team'], '#555')

    return render(request, 'gacha.html', {
        'driver': driver,
        'team_color': team_color,
        'pool_empty': False,
    })


def sign_driver(request, id):
    """簽約：確認招募車手"""
    driver = get_object_or_404(Driver, id=id)
    driver.is_signed = True
    driver.save()
    return redirect('home')


def discard_driver(request, id):
    """放棄：不簽約，從 DB 刪除暫存紀錄"""
    driver = get_object_or_404(Driver, id=id)
    driver.delete()
    return redirect('home')


def fire_driver(request, id):
    """解約：將已簽約車手移出車庫"""
    driver = get_object_or_404(Driver, id=id)
    driver.is_signed = False
    driver.save()
    return redirect('home')


def driver_detail(request, id):
    """車手獨立資訊頁：動態路由展示單一車手詳細資料"""
    driver = get_object_or_404(Driver, id=id)
    team_color = TEAM_COLORS.get(driver.team, '#555')
    return render(request, 'driver_detail.html', {'driver': driver, 'team_color': team_color})
