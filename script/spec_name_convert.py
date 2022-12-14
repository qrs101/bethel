import json

a = {
    "女上装": "WOMEN_CLOTHING_SIZE",
    "女上装-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女下装": "WOMEN_CLOTHING_SIZE",
    "女下装-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女士内裤-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女士内裤-常规": "WOMEN_CLOTHING_SIZE",
    "女士短裙-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女士短裙-常规": "WOMEN_CLOTHING_SIZE",
    "女士紧身衣-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女士连体裤-常规": "WOMEN_CLOTHING_SIZE",
    "女士连身泳衣-常规": "WOMEN_CLOTHING_SIZE",
    "女套装": "WOMEN_CLOTHING_SIZE",
    "女套装-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "女鞋": "SHOE_SIZE",
    "文胸": "BRA_SIZE",
    "男上装": "MEN_TOP_SIZE",
    "男下装": "MEN_BOTTOM_SIZE",
    "男士内裤": "MEN_CLOTHING_SIZE",
    "男士连体裤": "MEN_BOTTOM_SIZE",
    "男套装": "MEN_CLOTHING_SIZE",
    "男女套装": "CLOTHING_SIZE",
    "男鞋": "SHOE_SIZE",
    "童装": "KID_CLOTHING_SIZE",
    "童鞋": "SHOE_SIZE",
    "连衣裙": "WOMEN_CLOTHING_SIZE",
    "连衣裙-大码": "WOMEN_PLUS_CLOTHING_SIZE",
    "鞋子": "SHOE_SIZE"
}

s = 'WOMEN_CLOTHING_SIZE'
s.lower().replace('_', ' ')

for k, v in a.items():
	new_size = []
	for name in v.lower().replace('men', 'men\'s').split('_'):
		name = name[0].upper() + name[1:]
		new_size.append(name)
	v = ' '.join(new_size)
	#v = v.lower().replace('_', ' ')
	a[k] = v

b = json.dumps(a, ensure_ascii=False)
print(a)
print(b)