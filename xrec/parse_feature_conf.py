import re, copy, queue, json

class Parse(object):
	__patterns = [
		# pattern def
		r"""
			\s*  def 
			\s*  { 
			\s*  name    \s*  :  \s*  \".+\"
			\s*  op      \s*  :  \s*  \".+\"
			\s*  params  \s*  :  \s*  \".*\"
			\s*  } 
		""",
		# pattern feature
		r"""
			\s*  feature
			\s*  {
			\s*  (\s*  tag               \s*  :  \s* \d+)*                    # 匹配tag
			\s*  (\s*  setup_properties  \s*  :  \s*  \"  [^\s^"]+  \")?      # 匹配setup_properties
			\s*  def  \s*  :                                                  # 匹配def
			\s*    \"
			\s*      \$?[a-zA-Z0-9_]+  \s*  (,  \s*  \$?[a-zA-Z0-9_]+)*  \s*  =
			\s*      \@?[a-zA-Z0-9_]+  \(  \s*[^\s]+  \s*(,\s*  [^\s]+)*  \)
			\s*      ->  \s*  [^\s]+  \s*  (,\s*[^\s]+)*
			\s*      >>  \s*  [^\s]+
			\s*    \"
			\s*  (default_values \s* : \s* \" [a-zA-Z0-9_]+ \")?              # default_values
			\s*  }
		"""
	]

	@classmethod
	def get_pattern(cls):
		return cls.__patterns

	@classmethod
	def parse_fg_conf(cls, data):
		# 去除注释
		data = re.sub(r'#.*\n', '\n', data).strip()

		patterns = "|".join(cls.__patterns)

		# 检查是否符合语法
		r = re.match(f'({patterns})+', data, flags=re.X)
		if len(data) != r.span()[1]:
			raise ValueError(f"error fg, at: {data[r.span()[1]: r.span()[1] + 30]}")

		# 解析所有feature和def
		r = re.finditer(f'({patterns})', data, flags=re.X)

		return [feature.group().strip() for feature in r]

	@classmethod
	def parse_tag(cls, feature):
		pattern = r'(tag\s*:\s*\d+)'
		tags = re.findall(pattern, feature)
		return [int(tag.split(':')[1].strip()) for tag in tags]

	@classmethod
	def parse_def(cls, feature):
		try:
			feature_def = re.search(r"[^\"]*=[^\"]*->[^\"]*>>[^\"]", feature, flags=re.X).group()
			r = re.split(r"(=|->|>>)", feature_def)
			names = [name.strip() for name in r[0].split(',')]
			types = [typo.strip() for typo in r[4].split(',')]
			father_names = []
			is_user_feature = False
			is_item_feature = False
			if '@' not in r[2]:
				tmp = re.search(r'\(.*\)', r[2]).group()[1: -1]
				father_names = [father_name.strip() for father_name in tmp.split(',')]
			else:
				if 'user' in r[2] or 'context' in r[2]:
					is_user_feature = True
				if 'item' in r[2]:
					is_item_feature = True
		except AttributeError:
			print(f'feature: {feature}')

		return names, types, father_names, is_user_feature, is_item_feature

	@classmethod
	def parse_feature(cls, features):
		feature_dic = {}
		for feature in features:
			feature = feature.strip()
			if feature.startswith('def'):
				r = re.search(r'name\s*:\s\"[^\"]*\"', feature)
				name = r.group().split(":")[1].strip()[1:-1]
				if name in feature_dic.keys():
					raise ValueError(f'duplicate feature: {feature}')

				feature_dic[name] = Feature(name=name)
				continue

			try:
				tags = cls.parse_tag(feature)
				names, types, father_names, is_user, is_item = cls.parse_def(feature)
				for idx, name in enumerate(names):
					if name.startswith('$'):
						name = name[1:]
						tag = None
					else:
						tag = tags[idx]
					typo = types[idx]
					if name in feature_dic.keys():
						raise ValueError(f'duplicate feature: {feature}')
					feature_obj = Feature(tag=tag, name=name, typo=typo, is_user=is_user, is_item=is_item,
					                      father_name=copy.deepcopy(father_names))
					feature_dic[name] = feature_obj
			except re.error:
				print(f"error, feature: {feature}")
				break

		return feature_dic

class Feature(object):
	def __init__(self, tag=None, name=None, typo=None, father_name=[], default_value=None, is_user=False, is_item=False):
		self.tag = tag
		self.name = name
		self.type = typo
		self.default_value = default_value
		self.father_name = father_name
		self.father_feature = []
		self.root_feature = []
		self.is_user_feature = is_user
		self.is_item_feature = is_item

	def is_root(self):
		return len(self.father_feature) == 0

	def add_father_feature(self, feature_obj):
		self.father_feature.append(feature_obj)

	def init_root_feature(self):
		q = queue.Queue()
		q.put(self)
		s = set()
		s.add(self.name)
		while not q.empty():
			feature_obj = q.get()
			if feature_obj.is_root():
				self.root_feature.append(feature_obj)
			for tmp_obj in feature_obj.father_feature:
				if tmp_obj.name not in s:
					s.add(tmp_obj.name)
					q.put(tmp_obj)

	def show(self):
		print(f'name:{self.name}, tag:{self.tag}, type:{self.type}, father_feature:{self.father_name}')

def parse(path):
	with open(path, 'r') as fo:
		conf = fo.read()

	features = Parse.parse_fg_conf(conf)
	feature_dic = Parse.parse_feature(features)
	print(f'{len(feature_dic)} features')

	for name, feature_obj in feature_dic.items():
		for fn in feature_obj.father_name:
			feature_obj.add_father_feature(feature_dic[fn])

	for name, feature_obj in feature_dic.items():
		feature_obj.init_root_feature()

	return feature_dic

feature_dic = parse('./data/fg.conf')
# feature_dic: <key:name, value:Feature_object>

user_root = set()
item_root = set()

with open('./data/a.json') as fo:
	j = json.loads(fo.read())
	column = []
	#column += j['user_column'] + j['item_column'] + j['cross_column']
	column += j['cross_column']
	column = [
        "log_count_all_item_pvseq_7d_today",
        "log_count_all_cat3_pvseq_7d_today",
        "log_count_all_cat1_pvseq_7d_today",
        "log_count_all_mall_pvseq_7d_today",
        "hit_oz_all_item_pvseq_7d_today",
        "hit_oz_all_cat3_pvseq_7d_today",
        "hit_oz_all_cat1_pvseq_7d_today",
        "hit_oz_all_mall_pvseq_7d_today",
        "log_count_all_item_pvseq_1d",
        "log_count_all_cat3_pvseq_1d",
        "log_count_all_cat1_pvseq_1d",
        "log_count_all_mall_pvseq_1d",
        "hit_oz_all_item_pvseq_1d",
        "hit_oz_all_cat3_pvseq_1d",
        "hit_oz_all_cat1_pvseq_1d",
        "hit_oz_all_mall_pvseq_1d",
        "log_count_all_item_pvseq_3d",
        "log_count_all_cat3_pvseq_3d",
        "log_count_all_cat1_pvseq_3d",
        "log_count_all_mall_pvseq_3d",
        "hit_oz_all_item_pvseq_3d",
        "hit_oz_all_cat3_pvseq_3d",
        "hit_oz_all_cat1_pvseq_3d",
        "hit_oz_all_mall_pvseq_3d",
        "log_count_all_item_pvseq_7d",
        "log_count_all_cat3_pvseq_7d",
        "log_count_all_cat1_pvseq_7d",
        "log_count_all_mall_pvseq_7d",
        "hit_oz_all_item_pvseq_7d",
        "hit_oz_all_cat3_pvseq_7d",
        "hit_oz_all_cat1_pvseq_7d",
        "hit_oz_all_mall_pvseq_7d",
        "log_count_all_item_ipvseq_30d_today",
        "log_count_all_cat3_ipvseq_30d_today",
        "log_count_all_cat1_ipvseq_30d_today",
        "log_count_all_mall_ipvseq_30d_today",
        "hit_oz_all_item_ipvseq_30d_today",
        "hit_oz_all_cat3_ipvseq_30d_today",
        "hit_oz_all_cat1_ipvseq_30d_today",
        "hit_oz_all_mall_ipvseq_30d_today",
        "log_count_all_item_ipvseq_1d",
        "log_count_all_cat3_ipvseq_1d",
        "log_count_all_cat1_ipvseq_1d",
        "log_count_all_mall_ipvseq_1d",
        "hit_oz_all_item_ipvseq_1d",
        "hit_oz_all_cat3_ipvseq_1d",
        "hit_oz_all_cat1_ipvseq_1d",
        "hit_oz_all_mall_ipvseq_1d",
        "log_count_all_item_ipvseq_3d",
        "log_count_all_cat3_ipvseq_3d",
        "log_count_all_cat1_ipvseq_3d",
        "log_count_all_mall_ipvseq_3d",
        "hit_oz_all_item_ipvseq_3d",
        "hit_oz_all_cat3_ipvseq_3d",
        "hit_oz_all_cat1_ipvseq_3d",
        "hit_oz_all_mall_ipvseq_3d",
        "log_count_all_item_ipvseq_7d",
        "log_count_all_cat3_ipvseq_7d",
        "log_count_all_cat1_ipvseq_7d",
        "log_count_all_mall_ipvseq_7d",
        "hit_oz_all_item_ipvseq_7d",
        "hit_oz_all_cat3_ipvseq_7d",
        "hit_oz_all_cat1_ipvseq_7d",
        "hit_oz_all_mall_ipvseq_7d",
        "log_count_all_item_ipvseq_15d",
        "log_count_all_cat3_ipvseq_15d",
        "log_count_all_cat1_ipvseq_15d",
        "log_count_all_mall_ipvseq_15d",
        "hit_oz_all_item_ipvseq_15d",
        "hit_oz_all_cat3_ipvseq_15d",
        "hit_oz_all_cat1_ipvseq_15d",
        "hit_oz_all_mall_ipvseq_15d",
        "log_count_all_item_buyseq_400d_today",
        "log_count_all_cat3_buyseq_400d_today",
        "log_count_all_cat1_buyseq_400d_today",
        "log_count_all_mall_buyseq_400d_today",
        "hit_oz_all_item_buyseq_400d_today",
        "hit_oz_all_cat3_buyseq_400d_today",
        "hit_oz_all_cat1_buyseq_400d_today",
        "hit_oz_all_mall_buyseq_400d_today",
        "log_count_all_item_buyseq_1d",
        "log_count_all_cat3_buyseq_1d",
        "log_count_all_cat1_buyseq_1d",
        "log_count_all_mall_buyseq_1d",
        "hit_oz_all_item_buyseq_1d",
        "hit_oz_all_cat3_buyseq_1d",
        "hit_oz_all_cat1_buyseq_1d",
        "hit_oz_all_mall_buyseq_1d",
        "log_count_all_item_buyseq_3d",
        "log_count_all_cat3_buyseq_3d",
        "log_count_all_cat1_buyseq_3d",
        "log_count_all_mall_buyseq_3d",
        "hit_oz_all_item_buyseq_3d",
        "hit_oz_all_cat3_buyseq_3d",
        "hit_oz_all_cat1_buyseq_3d",
        "hit_oz_all_mall_buyseq_3d",
        "log_count_all_item_buyseq_7d",
        "log_count_all_cat3_buyseq_7d",
        "log_count_all_cat1_buyseq_7d",
        "log_count_all_mall_buyseq_7d",
        "hit_oz_all_item_buyseq_7d",
        "hit_oz_all_cat3_buyseq_7d",
        "hit_oz_all_cat1_buyseq_7d",
        "hit_oz_all_mall_buyseq_7d",
        "log_count_all_item_buyseq_15d",
        "log_count_all_cat3_buyseq_15d",
        "log_count_all_cat1_buyseq_15d",
        "log_count_all_mall_buyseq_15d",
        "hit_oz_all_item_buyseq_15d",
        "hit_oz_all_cat3_buyseq_15d",
        "hit_oz_all_cat1_buyseq_15d",
        "hit_oz_all_mall_buyseq_15d",
        "log_count_all_item_buyseq_100d",
        "log_count_all_cat3_buyseq_100d",
        "log_count_all_cat1_buyseq_100d",
        "log_count_all_mall_buyseq_100d",
        "hit_oz_all_item_buyseq_100d",
        "hit_oz_all_cat3_buyseq_100d",
        "hit_oz_all_cat1_buyseq_100d",
        "hit_oz_all_mall_buyseq_100d",
        "log_count_all_item_buyseq_300d",
        "log_count_all_cat3_buyseq_300d",
        "log_count_all_cat1_buyseq_300d",
        "log_count_all_mall_buyseq_300d",
        "hit_oz_all_item_buyseq_300d",
        "hit_oz_all_cat3_buyseq_300d",
        "hit_oz_all_cat1_buyseq_300d",
        "hit_oz_all_mall_buyseq_300d",
        "log_count_all_item_favseq_400d_today",
        "log_count_all_cat3_favseq_400d_today",
        "log_count_all_cat1_favseq_400d_today",
        "log_count_all_mall_favseq_400d_today",
        "hit_oz_all_item_favseq_400d_today",
        "hit_oz_all_cat3_favseq_400d_today",
        "hit_oz_all_cat1_favseq_400d_today",
        "hit_oz_all_mall_favseq_400d_today",
        "log_count_all_item_favseq_1d",
        "log_count_all_cat3_favseq_1d",
        "log_count_all_cat1_favseq_1d",
        "log_count_all_mall_favseq_1d",
        "hit_oz_all_item_favseq_1d",
        "hit_oz_all_cat3_favseq_1d",
        "hit_oz_all_cat1_favseq_1d",
        "hit_oz_all_mall_favseq_1d",
        "log_count_all_item_favseq_3d",
        "log_count_all_cat3_favseq_3d",
        "log_count_all_cat1_favseq_3d",
        "log_count_all_mall_favseq_3d",
        "hit_oz_all_item_favseq_3d",
        "hit_oz_all_cat3_favseq_3d",
        "hit_oz_all_cat1_favseq_3d",
        "hit_oz_all_mall_favseq_3d",
        "log_count_all_item_favseq_7d",
        "log_count_all_cat3_favseq_7d",
        "log_count_all_cat1_favseq_7d",
        "log_count_all_mall_favseq_7d",
        "hit_oz_all_item_favseq_7d",
        "hit_oz_all_cat3_favseq_7d",
        "hit_oz_all_cat1_favseq_7d",
        "hit_oz_all_mall_favseq_7d",
        "log_count_all_item_favseq_15d",
        "log_count_all_cat3_favseq_15d",
        "log_count_all_cat1_favseq_15d",
        "log_count_all_mall_favseq_15d",
        "hit_oz_all_item_favseq_15d",
        "hit_oz_all_cat3_favseq_15d",
        "hit_oz_all_cat1_favseq_15d",
        "hit_oz_all_mall_favseq_15d",
        "log_count_all_item_favseq_100d",
        "log_count_all_cat3_favseq_100d",
        "log_count_all_cat1_favseq_100d",
        "log_count_all_mall_favseq_100d",
        "hit_oz_all_item_favseq_100d",
        "hit_oz_all_cat3_favseq_100d",
        "hit_oz_all_cat1_favseq_100d",
        "hit_oz_all_mall_favseq_100d",
        "log_count_all_item_favseq_300d",
        "log_count_all_cat3_favseq_300d",
        "log_count_all_cat1_favseq_300d",
        "log_count_all_mall_favseq_300d",
        "hit_oz_all_item_favseq_300d",
        "hit_oz_all_cat3_favseq_300d",
        "hit_oz_all_cat1_favseq_300d",
        "hit_oz_all_mall_favseq_300d"
    ]
	for name in column:
		if name not in feature_dic.keys():
			continue
		for tmp in feature_dic[name].root_feature:
			if tmp.tag is not None:
				if tmp.is_user_feature:
					user_root.add(tmp.name)
				else:
					item_root.add(tmp.name)


'''
for key, value in feature_dic.items():
	for tmp in value.root_feature:
		if tmp.tag is not None:
			if tmp.is_user_feature:
				user_root.add(tmp.name)
			else:
				item_root.add(tmp.name)

'''
print(user_root)
print(item_root)
