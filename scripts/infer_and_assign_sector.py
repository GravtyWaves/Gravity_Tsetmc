# Script to infer and assign sector for symbols without sector using their name
import re
from app.db import SessionLocal, SymbolList, Sector
from persiantools import characters

# Heuristic rules for sector assignment (expanded based on missing sectors)
SECTOR_RULES = [
    (re.compile(r"بیمه"), "بیمه و بازنشستگی"),
    (re.compile(r"بانک"), "بانک"),
    (re.compile(r"سرمایه ?گذاری"), "سرمایه گذاری"),
    (re.compile(r"دارو|دارویی"), "دارویی"),
    (re.compile(r"فلز|فلزی"), "فلزات اساسی"),
    (re.compile(r"شیمیایی"), "شیمیایی"),
    (re.compile(r"خودرو"), "خودرو"),
    (re.compile(r"سیمان"), "سیمان"),
    (re.compile(r"غذا|غذایی"), "غذایی"),
    (re.compile(r"کاشی|سرامیک"), "کاشی و سرامیک"),
    (re.compile(r"رایانه|اطلاعات|ارتباطات"), "رایانه"),
    (re.compile(r"حمل و نقل|ترابری"), "حمل و نقل"),
    (re.compile(r"لاستیک"), "لاستیک"),
    (re.compile(r"قند|شکر"), "قند و شکر"),
    (re.compile(r"انبوه سازی|ساختمان"), "انبوه سازی"),
    (re.compile(r"ماشین آلات"), "ماشین آلات"),
    (re.compile(r"کانی فلزی"), "کانی فلزی"),
    (re.compile(r"کانی غیر فلزی"), "کانی غیر فلزی"),
    (re.compile(r"ذغال سنگ"), "ذغال سنگ"),
    (re.compile(r"فرآورده های نفتی|پالایش"), "فرآورده های نفتی"),
    (re.compile(r"محصولات فلزی"), "محصولات فلزی"),
    (re.compile(r"محصولات چوبی"), "محصولات چوبی"),
    (re.compile(r"محصولات چرمی"), "محصولات چرمی"),
    (re.compile(r"محصولات کاغذی"), "محصولات کاغذی"),
    (re.compile(r"انتشار|چاپ"), "انتشار و چاپ"),
    (re.compile(r"منسوجات"), "منسوجات"),
    (re.compile(r"سایر مالی"), "سایر مالی"),
    (re.compile(r"مالی"), "مالی"),
    (re.compile(r"اداره بازارهای مالی"), "اداره بازارهای مالی"),
    (re.compile(r"فنی مهندسی"), "فنی مهندسی"),
    (re.compile(r"استخراج نفت"), "استخراج نفت"),
    (re.compile(r"لیزینگ"), "سایر مالی"),
    (re.compile(r"نفت|پالایش"), "فرآورده های نفتی"),
    (re.compile(r"لبنیات|شیر|گلوکوزان"), "غذایی"),
    (re.compile(r"کاشی|سرامیک"), "کاشی و سرامیک"),
    (re.compile(r"شیشه"), "کانی غیر فلزی"),
    (re.compile(r"ذغال سنگ"), "ذغال سنگ"),
    (re.compile(r"نسوز"), "کانی غیر فلزی"),
    (re.compile(r"الکتریک|برق"), "تامین آب، برق و گاز"),
    (re.compile(r"نیروگاه|تولید نیروی برق"), "تامین آب، برق و گاز"),
    (re.compile(r"کشت و صنعت|کشاورزی"), "زراعت"),
    (re.compile(r"فرآورده های دامی"), "غذایی"),
    (re.compile(r"صنعتی"), "فلزات اساسی"),  # Broad, but many are industrial
    (re.compile(r"معدنی"), "کانی فلزی"),
    (re.compile(r"کارخانجات"), "فلزات اساسی"),  # Broad
    (re.compile(r"تولیدی"), "فلزات اساسی"),  # Broad
    (re.compile(r"گسترش صنایع"), "فلزات اساسی"),
    (re.compile(r"تراکتورسازی"), "ماشین آلات"),
    (re.compile(r"کمباین"), "ماشین آلات"),
    (re.compile(r"پمپ"), "ماشین آلات"),
    (re.compile(r"تجهیزات سنگین"), "ماشین آلات"),
    (re.compile(r"ماشین سازی"), "ماشین آلات"),
    (re.compile(r"مهندسی"), "فنی مهندسی"),
    (re.compile(r"بازرسی"), "فنی مهندسی"),
    (re.compile(r"نساجی"), "منسوجات"),
    (re.compile(r"پشمبافی"), "منسوجات"),
    (re.compile(r"نخریسی"), "منسوجات"),
    (re.compile(r"فرهنگی ورزشی"), "سایر مالی"),  # Sports clubs
    (re.compile(r"اقتصادی"), "سرمایه گذاری"),
    (re.compile(r"مدیریت سرمایه"), "سرمایه گذاری"),
    (re.compile(r"صندوق بازنشستگی"), "بیمه و بازنشستگی"),
    (re.compile(r"بازنشستگی"), "بیمه و بازنشستگی"),
    (re.compile(r"تامین اجتماعی"), "بیمه و بازنشستگی"),
    (re.compile(r"اتکایی"), "بیمه و بازنشستگی"),
    (re.compile(r"زندگی"), "بیمه و بازنشستگی"),
    (re.compile(r"تجارت نو"), "بیمه و بازنشستگی"),
    (re.compile(r"پاسارگاد"), "بیمه و بازنشستگی"),
    (re.compile(r"سامان"), "بیمه و بازنشستگی"),
    (re.compile(r"آسیا"), "بیمه و بازنشستگی"),
    (re.compile(r"البرز"), "بیمه و بازنشستگی"),
    (re.compile(r"پارسیان"), "بیمه و بازنشستگی"),
    (re.compile(r"دانا"), "بیمه و بازنشستگی"),
    (re.compile(r"ما"), "بیمه و بازنشستگی"),
    (re.compile(r"ملت"), "بیمه و بازنشستگی"),
    (re.compile(r"کارآفرین"), "بیمه و بازنشستگی"),
    (re.compile(r"امید"), "بیمه و بازنشستگی"),
    (re.compile(r"ایرانیان"), "بیمه و بازنشستگی"),
    (re.compile(r"توسعه ملی"), "بانک"),
    (re.compile(r"صادرات"), "بانک"),
    (re.compile(r"پارسیان"), "بانک"),
    (re.compile(r"پاسارگاد"), "بانک"),
    (re.compile(r"پست بانک"), "بانک"),
    (re.compile(r"تجارت"), "بانک"),
    (re.compile(r"توشه"), "سرمایه گذاری"),
    (re.compile(r"خاورمیانه"), "بانک"),
    (re.compile(r"سینا"), "بانک"),
    (re.compile(r"غدیر"), "سرمایه گذاری"),
    (re.compile(r"کارآفرین"), "بانک"),
    (re.compile(r"ص. معادن"), "کانی فلزی"),
    (re.compile(r"لیزینگ"), "سایر مالی"),
    (re.compile(r"واسپاری"), "سایر مالی"),
    (re.compile(r"اقتصاد نوین"), "بانک"),
    (re.compile(r"صنعت نفت"), "استخراج نفت"),
    (re.compile(r"نیرو"), "تامین آب، برق و گاز"),
    (re.compile(r"ملی ایران"), "سرمایه گذاری"),
    (re.compile(r"نشاسته"), "غذایی"),
    (re.compile(r"گلوکز"), "غذایی"),
    (re.compile(r"الکترونیک"), "دستگاه های برقی"),
    (re.compile(r"ساختمان"), "انبوه سازی"),
    (re.compile(r"تاسیسات"), "انبوه سازی"),
    (re.compile(r"پیوند"), "تامین آب، برق و گاز"),
    (re.compile(r"مولد"), "تامین آب، برق و گاز"),
    (re.compile(r"بهپاک"), "شیمیایی"),
    (re.compile(r"تبرک"), "فلزات اساسی"),
    (re.compile(r"کشتیرانی"), "حمل و نقل"),
    (re.compile(r"دریای خزر"), "حمل و نقل"),
    (re.compile(r"آریا"), "حمل و نقل"),
    (re.compile(r"سامان"), "بانک"),
    (re.compile(r"شمس"), "تامین آب، برق و گاز"),
    (re.compile(r"بهار رز"), "زراعت"),
    (re.compile(r"دانه روغنی"), "زراعت"),
    (re.compile(r"پاکدیس"), "غذایی"),
    (re.compile(r"شهداب"), "زراعت"),
    (re.compile(r"صنعتی مینو"), "فلزات اساسی"),
    (re.compile(r"خمیرمایه"), "غذایی"),
    (re.compile(r"ویتانا"), "غذایی"),
    (re.compile(r"قند"), "قند و شکر"),
    (re.compile(r"شیروان"), "قند و شکر"),
    (re.compile(r"بیستون"), "قند و شکر"),
    (re.compile(r"تربت جام"), "قند و شکر"),
    (re.compile(r"نقش جهان"), "قند و شکر"),
    (re.compile(r"تربت حیدریه"), "قند و شکر"),
    (re.compile(r"ارومیه"), "قند و شکر"),
    (re.compile(r"چارمحال"), "قند و شکر"),
    (re.compile(r"چهارمحال"), "قند و شکر"),
    (re.compile(r"معدنکاران"), "کانی فلزی"),
    (re.compile(r"فرانسوز"), "کاشی و سرامیک"),
    (re.compile(r"زغال سنگ"), "ذغال سنگ"),
    (re.compile(r"پروده"), "ذغال سنگ"),
    (re.compile(r"طبس"), "ذغال سنگ"),
    (re.compile(r"کربن"), "کانی غیر فلزی"),
    (re.compile(r"صنعتی و معدنی"), "کانی فلزی"),
    (re.compile(r"شاهرود"), "کانی فلزی"),
    (re.compile(r"بازرگانی"), "خرده فروشی"),
    (re.compile(r"مرجان"), "خرده فروشی"),
    (re.compile(r"گلدیران"), "فلزات اساسی"),
    (re.compile(r"مادیران"), "فلزات اساسی"),
    (re.compile(r"ایران - معین"), "بیمه و بازنشستگی"),
    (re.compile(r"میهن"), "بیمه و بازنشستگی"),
    (re.compile(r"رضوی"), "غذایی"),
    (re.compile(r"خسروی"), "منسوجات"),
    (re.compile(r"عطرین"), "منسوجات"),
    (re.compile(r"نوین"), "بیمه و بازنشستگی"),
    (re.compile(r"نیان"), "دستگاه های برقی"),
    (re.compile(r"نیشکر"), "زراعت"),
    (re.compile(r"تعاون"), "بیمه و بازنشستگی"),
    (re.compile(r"دی"), "بیمه و بازنشستگی"),
    (re.compile(r"سپهر"), "سرمایه گذاری"),
    (re.compile(r"گردشگری"), "بانک"),
    (re.compile(r"بهمن"), "سایر مالی"),
    (re.compile(r"تجار"), "سایر مالی"),
    (re.compile(r"ایران و شرق"), "سایر مالی"),
    (re.compile(r"مپنا"), "تامین آب، برق و گاز"),
    (re.compile(r"معلم"), "بیمه و بازنشستگی"),
    (re.compile(r"ملل"), "بانک"),
    (re.compile(r"هور"), "تامین آب، برق و گاز"),
    (re.compile(r"سرام"), "کاشی و سرامیک"),
    (re.compile(r"استقلال"), "فرهنگی ورزشی"),
    (re.compile(r"پرسپولیس"), "فرهنگی ورزشی"),
    (re.compile(r"میلاد"), "سرمایه گذاری"),
    (re.compile(r"پردیس"), "بیمه و بازنشستگی"),
    (re.compile(r"حکمت"), "بیمه و بازنشستگی"),
    (re.compile(r"پتروشیمی"), "شیمیایی"),
    (re.compile(r"شوکو"), "غذایی"),
    (re.compile(r"رازی"), "بیمه و بازنشستگی"),
    (re.compile(r"دی"), "بانک"),
    (re.compile(r"صدف"), "کاشی و سرامیک"),
    (re.compile(r"مینا"), "کانی غیر فلزی"),
    (re.compile(r"خاک نسوز"), "کانی غیر فلزی"),
    (re.compile(r"فارسیت"), "فلزات اساسی"),
    (re.compile(r"مخابراتی"), "وسایل ارتباطی"),
    (re.compile(r"آزمایش"), "فلزات اساسی"),
    (re.compile(r"قزوین"), "کانی غیر فلزی"),
    (re.compile(r"پیام"), "فلزات اساسی"),
    (re.compile(r"سرمایه"), "بانک"),
    (re.compile(r"دریایی"), "حمل و نقل"),
    (re.compile(r"گرانیت"), "کانی غیر فلزی"),
    (re.compile(r"رسالت"), "بانک"),
    (re.compile(r"نگین"), "سرمایه گذاری"),
    (re.compile(r"اتکایی سامان"), "بیمه و بازنشستگی"),
    (re.compile(r"لیا"), "شیمیایی"),
    (re.compile(r"شیرین"), "زراعت"),
    (re.compile(r"زنگان"), "تامین آب، برق و گاز"),
    (re.compile(r"هنر"), "سرمایه گذاری"),
    (re.compile(r"ایتالران"), "فلزات اساسی"),
    (re.compile(r"لوازم خانگی"), "فلزات اساسی"),
    (re.compile(r"بهاران"), "زراعت"),
    (re.compile(r"شهر"), "بانک"),
    (re.compile(r"بازرسی"), "فنی مهندسی"),
    (re.compile(r"آذریت"), "زراعت"),
    (re.compile(r"ایرانیت"), "فلزات اساسی"),
    (re.compile(r"هامرز"), "بیمه و بازنشستگی"),
    (re.compile(r"آریا دانا"), "سایر مالی"),
    (re.compile(r"هپکو"), "ماشین آلات"),
    (re.compile(r"ورزیران"), "زراعت"),
    (re.compile(r"آینده"), "بانک"),
    (re.compile(r"سرمد"), "بیمه و بازنشستگی"),
    (re.compile(r"باران"), "بیمه و بازنشستگی"),
    (re.compile(r"بروجرد"), "منسوجات"),
    (re.compile(r"آگاه"), "بیمه و بازنشستگی"),
    (re.compile(r"نیرو محرکه"), "ماشین آلات"),
    (re.compile(r"ماهتاب"), "تامین آب، برق و گاز"),
    (re.compile(r"حافظ"), "بیمه و بازنشستگی"),
    (re.compile(r"اتمسفر"), "فلزات اساسی"),
    (re.compile(r"افشار"), "منسوجات"),
    (re.compile(r"فیروزا"), "فنی مهندسی"),
    (re.compile(r"توس"), "منسوجات"),
    (re.compile(r"سینا"), "بیمه و بازنشستگی"),
    (re.compile(r"آزادگان"), "سرمایه گذاری"),
    (re.compile(r"سیمان"), "سیمان"),
    (re.compile(r"آوای پارس"), "بیمه و بازنشستگی"),
    (re.compile(r"تهران"), "بیمه و بازنشستگی"),
    (re.compile(r"مارگارین"), "غذایی"),
    (re.compile(r"آرمان"), "بیمه و بازنشستگی"),
    (re.compile(r"آبگینه"), "کانی غیر فلزی"),
    (re.compile(r"روغن نباتی"), "غذایی"),
    (re.compile(r"رایا"), "بیمه و بازنشستگی"),
]

def normalize(text):
    return characters.ar_to_fa(''.join(str(text).split())).strip()

def get_valid_sectors(session):
    return {normalize(s.sector_name): s.sector_id for s in session.query(Sector).all()}

def guess_sector(name, ticker, valid_sectors):
    # Check if ticker starts with 'غ' for food sector
    if ticker and ticker.startswith('غ'):
        return valid_sectors.get(normalize("غذایی"))
    # Check if ticker starts with 'ق' for sugar sector
    if ticker and ticker.startswith('ق'):
        return valid_sectors.get(normalize("قند و شکر"))
    
    name_norm = normalize(name)
    if "بیمه" in name_norm:
        return valid_sectors.get(normalize("بیمه و بازنشستگی"))
    if "بانک" in name_norm or "گردشگری" in name_norm or "اقتصاد" in name_norm or "دی" in name_norm or "سامان" in name_norm or "ملت" in name_norm or "ملل" in name_norm or "شهر" in name_norm or "آینده" in name_norm or "سرمایه" in name_norm or "رسالت" in name_norm or "قرض الحسنه" in name_norm:
        return valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط"))
    if "تولیدنیرویبرق" in name_norm:
        return valid_sectors.get(normalize("تامین آب، برق و گاز"))
    if "کشتوصنعت" in name_norm:
        return valid_sectors.get(normalize("زراعت و خدمات وابسته"))
    if "نفت" in name_norm:
        return valid_sectors.get(normalize("فرآورده های نفتی"))
    if "قند" in name_norm:
        return valid_sectors.get(normalize("قند و شکر"))
    if "سیمان" in name_norm:
        return valid_sectors.get(normalize("سیمان، آهک و گچ"))
    if "خودرو" in name_norm:
        return valid_sectors.get(normalize("خودرو و ساخت قطعات"))
    if "شیمیایی" in name_norm:
        return valid_sectors.get(normalize("محصولات شیمیایی"))
    if "فلزاتاساسی" in name_norm:
        return valid_sectors.get(normalize("فلزات اساسی"))
    if "غذایی" in name_norm:
        return valid_sectors.get(normalize("غذایی"))
    if "کاشی" in name_norm:
        return valid_sectors.get(normalize("سیمان، آهک و گچ"))
    if "لیزینگ" in name_norm or "واسپاری" in name_norm:
        return valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط"))
    if "سرمایهگذاری" in name_norm or "مدیریت سرمایه" in name_norm or "صندوق بازنشستگی" in name_norm or "بازنشستگی" in name_norm or "تامین اجتماعی" in name_norm or "اتکایی" in name_norm or "زندگی" in name_norm or "تجارت نو" in name_norm or "پاسارگاد" in name_norm or "سامان" in name_norm or "آسیا" in name_norm or "البرز" in name_norm or "پارسیان" in name_norm or "دانا" in name_norm or "ما" in name_norm or "ملت" in name_norm or "کارآفرین" in name_norm or "امید" in name_norm or "ایرانیان" in name_norm or "توسعه ملی" in name_norm or "صادرات" in name_norm or "پارسیان" in name_norm or "پاسارگاد" in name_norm or "پست بانک" in name_norm or "تجارت" in name_norm or "توشه" in name_norm or "خاورمیانه" in name_norm or "سینا" in name_norm or "غدیر" in name_norm or "کارآفرین" in name_norm or "ص. معادن" in name_norm or "اقتصاد نوین" in name_norm or "نیرو" in name_norm or "ملی ایران" in name_norm:
        return valid_sectors.get(normalize("سرمایه گذاریها"))
    if "دارویی" in name_norm:
        return valid_sectors.get(normalize("مواد و محصولات دارویی"))
    if "ماشین" in name_norm or "تراکتور" in name_norm or "کمباین" in name_norm or "تجهیزات سنگین" in name_norm or "نیرو محرکه" in name_norm:
        return valid_sectors.get(normalize("ماشین آلات و دستگاه های برقی"))
    if "رایانه" in name_norm:
        return valid_sectors.get(normalize("رایانه و فعالیت های وابسته به آن"))
    if "انبوهسازی" in name_norm:
        return valid_sectors.get(normalize("انبوه سازی، املاک و مستغلات"))
    if "حملونقل" in name_norm:
        return valid_sectors.get(normalize("حمل ونقل، انبارداری و ارتباطات"))
    if "ذغالسنگ" in name_norm:
        return valid_sectors.get(normalize("استخراج کانه های فلزی"))
    if "کانفلزی" in name_norm:
        return valid_sectors.get(normalize("استخراج کانه های فلزی"))
    if "کانغیرفلزی" in name_norm:
        return valid_sectors.get(normalize("سیمان، آهک و گچ"))
    if "منسوجات" in name_norm:
        return valid_sectors.get(normalize("محصولات کاغذی"))
    if "فرآوردههاینفتی" in name_norm:
        return valid_sectors.get(normalize("فرآورده های نفتی"))
    if "محصولاتفلزی" in name_norm:
        return valid_sectors.get(normalize("ساخت محصولات فلزی"))
    if "انتشار" in name_norm:
        return valid_sectors.get(normalize("انتشار، چاپ و تکثیر"))
    if "لاستیک" in name_norm:
        return valid_sectors.get(normalize("لاستیک و پلاستیک"))
    if "دستگاههایبرقی" in name_norm:
        return valid_sectors.get(normalize("ماشین آلات و دستگاه های برقی"))
    if "وسایلارتباطی" in name_norm:
        return valid_sectors.get(normalize("مخابرات"))
    if "سایرمالی" in name_norm:
        return valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط"))
    if "مالی" in name_norm:
        return valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط"))
    if "ادارهبازارهایمالی" in name_norm:
        return valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط"))
    if "فنیمهندسی" in name_norm:
        return valid_sectors.get(normalize("خدمات فنی و مهندسی"))
    if "استخراجنفت" in name_norm:
        return valid_sectors.get(normalize("استخراج نفت گاز و خدمات جنبی جز اکتشاف"))
    if "زراعت" in name_norm:
        return valid_sectors.get(normalize("زراعت و خدمات وابسته"))
    if "خردهنشینی" in name_norm:
        return valid_sectors.get(normalize("خرده فروشی،باستثنای وسایل نقلیه موتوری"))
    if "چندرشتهای" in name_norm:
        return valid_sectors.get(normalize("فلزات اساسی"))
    
    # Specific assignments for unmatched stocks
    specific_assignments = {
        "بفجر": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "تپمپی": valid_sectors.get(normalize("خودرو و ساخت قطعات")),
        "تکنو": valid_sectors.get(normalize("خودرو و ساخت قطعات")),
        "شستا": valid_sectors.get(normalize("سرمایه گذاریها")),
        "کاذر": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کپارس": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کپشیر": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کحافظ": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کخاک": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کساپا": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کساوه": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کسرام": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کسعدی": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کطبس": valid_sectors.get(normalize("استخراج کانه های فلزی")),
        "کفپارس": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کفرا": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کگاز": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کلوند": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کماسه": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کهمدا": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "لابسا": valid_sectors.get(normalize("خرده فروشی،باستثنای وسایل نقلیه موتوری")),
        "لپارس": valid_sectors.get(normalize("رایانه و فعالیت های وابسته به آن")),
        "لخزر": valid_sectors.get(normalize("رایانه و فعالیت های وابسته به آن")),
        "لسرما": valid_sectors.get(normalize("خرده فروشی،باستثنای وسایل نقلیه موتوری")),
        "مبین": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "محتشم": valid_sectors.get(normalize("محصولات کاغذی")),
        "نمرینو": valid_sectors.get(normalize("محصولات کاغذی")),
        "وامید": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وایران": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وبانک": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وبشهر": valid_sectors.get(normalize("سرمایه گذاریها")),
        "وبصادر": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وبملت": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وپارس": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وپاسار": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وپست": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وتجارت": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وتوشه": valid_sectors.get(normalize("سرمایه گذاریها")),
        "وخاور": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وسینا": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وصندوق": valid_sectors.get(normalize("سرمایه گذاریها")),
        "وغدیر": valid_sectors.get(normalize("سرمایه گذاریها")),
        "وکار": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وکغدیر": valid_sectors.get(normalize("سرمایه گذاریها")),
        "ولپارس": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولساپا": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولصنم": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولغدر": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولکار": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولملت": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولنوین": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ونوین": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ونیرو": valid_sectors.get(normalize("سرمایه گذاریها")),
        "ونیکی": valid_sectors.get(normalize("سرمایه گذاریها")),
        "آردینه": valid_sectors.get(normalize("غذایی")),
        "بالاس": valid_sectors.get(normalize("خدمات فنی و مهندسی")),
        "بپیوند": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "بجهرم": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "بزاگرس": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "بگیلان": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "بمپنا": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "بمولد": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "حخزر": valid_sectors.get(normalize("حمل ونقل، انبارداری و ارتباطات")),
        "سامان": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "شمس": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "عالیس": valid_sectors.get(normalize("غذایی")),
        "کانسار": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کایزد": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کپرور": valid_sectors.get(normalize("استخراج کانه های فلزی")),
        "کتوسعه": valid_sectors.get(normalize("سرمایه گذاریها")),
        "کربن": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کزغال": valid_sectors.get(normalize("استخراج کانه های فلزی")),
        "نخریس": valid_sectors.get(normalize("محصولات کاغذی")),
        "نطرین": valid_sectors.get(normalize("محصولات کاغذی")),
        "نیان": valid_sectors.get(normalize("رایانه و فعالیت های وابسته به آن")),
        "نیشکر": valid_sectors.get(normalize("قند و شکر")),
        "وسپهر": valid_sectors.get(normalize("سرمایه گذاریها")),
        "وگردش": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولبهمن": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولتجار": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ولشرق": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ومپنا": valid_sectors.get(normalize("خدمات فنی و مهندسی")),
        "وملل": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وهور": valid_sectors.get(normalize("سرمایه گذاریها")),
        "کارام": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "استقلال": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "پرسپولیس": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "بمیلا": valid_sectors.get(normalize("سرمایه گذاریها")),
        "حاریا": valid_sectors.get(normalize("حمل ونقل، انبارداری و ارتباطات")),
        "وپسا": valid_sectors.get(normalize("محصولات شیمیایی")),
        "ولراز": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "دی": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "کصدف": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کمینا": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کباده": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "کقزوی": valid_sectors.get(normalize("سیمان، آهک و گچ")),
        "سمایه": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "وسالت": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "گنگین": valid_sectors.get(normalize("سرمایه گذاریها")),
        "شلیا": valid_sectors.get(normalize("محصولات شیمیایی")),
        "شزنگ": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "وهنر": valid_sectors.get(normalize("سرمایه گذاریها")),
        "لخانه": valid_sectors.get(normalize("خرده فروشی،باستثنای وسایل نقلیه موتوری")),
        "وشهر": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "ساذری": valid_sectors.get(normalize("فلزات اساسی")),
        "ولانا": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "تپکو": valid_sectors.get(normalize("خودرو و ساخت قطعات")),
        "کورز": valid_sectors.get(normalize("خودرو و ساخت قطعات")),
        "وآیند": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "نبروج": valid_sectors.get(normalize("محصولات کاغذی")),
        "ولیز": valid_sectors.get(normalize("فعالیتهای کمکی به نهادهای مالی واسط")),
        "بکهنوج": valid_sectors.get(normalize("تامین آب، برق و گاز")),
        "تفیرو": valid_sectors.get(normalize("ماشین آلات و دستگاه های برقی")),
        "نتوس": valid_sectors.get(normalize("محصولات کاغذی")),
        "خودکفا": valid_sectors.get(normalize("سرمایه گذاریها")),
        "کفرآور": valid_sectors.get(normalize("سیمان، آهک و گچ")),
    }
    if ticker in specific_assignments:
        return specific_assignments[ticker]
    
    return None

def main():
    session = SessionLocal()
    # Ensure "غذایی" sector exists
    if not session.query(Sector).filter(Sector.sector_name == "غذایی").first():
        new_sector = Sector(sector_name="غذایی", sector_id=15508900928481581.0)  # From SECTOR_WEBID_MAP
        session.add(new_sector)
        session.commit()
    # Ensure "بیمه و بازنشستگی" sector exists
    if not session.query(Sector).filter(Sector.sector_name == "بیمه و بازنشستگی").first():
        new_sector = Sector(sector_name="بیمه و بازنشستگی", sector_id=59105676994811497.0)  # From SECTOR_WEBID_MAP
        session.add(new_sector)
        session.commit()
    # Ensure "فرآورده های نفتی" sector exists
    if not session.query(Sector).filter(Sector.sector_name == "فرآورده های نفتی").first():
        new_sector = Sector(sector_name="فرآورده های نفتی", sector_id=12331083953323969.0)  # From SECTOR_WEBID_MAP
        session.add(new_sector)
        session.commit()
    # Ensure "تامین آب، برق و گاز" sector exists
    if not session.query(Sector).filter(Sector.sector_name == "تامین آب، برق و گاز").first():
        new_sector = Sector(sector_name="تامین آب، برق و گاز", sector_id=54843635503648458.0)  # From SECTOR_WEBID_MAP
        session.add(new_sector)
        session.commit()
    # Ensure "قند و شکر" sector exists
    if not session.query(Sector).filter(Sector.sector_name == "قند و شکر").first():
        new_sector = Sector(sector_name="قند و شکر", sector_id=21948907150049163.0)  # From SECTOR_WEBID_MAP
        session.add(new_sector)
        session.commit()
    valid_sectors = get_valid_sectors(session)
    symbols = session.query(SymbolList).filter(SymbolList.sector_id == None).all()
    updated = 0
    for sym in symbols:
        sector_id = guess_sector(sym.name, sym.symbol_fa, valid_sectors)
        if sector_id:
            sym.sector_id = sector_id
            updated += 1
        else:
            print(f"No match for {sym.symbol_fa}: {sym.name}")
    session.commit()
    print(f"{updated} symbols updated with inferred sector.")
    session.close()

if __name__ == "__main__":
    main()
