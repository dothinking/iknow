import os
import shutil

# source and desination folder
source_posts = os.path.join(os.getcwd(), '_posts')
source_images = os.path.join(os.getcwd(), '_images')
dest_posts = r'D:/WorkSpace/Gitee/iknow/_posts'
dest_images = r'D:/WorkSpace/Gitee/iknow/public/uploads'

# keywords
keywords = {	
	'极限': ['趋于'], 
	'等价无穷小': [],
	'重要极限公式': [],
	'夹逼准则': [],
	'洛必达法则': ['洛必达'],
	'泰勒公式': ['泰勒'],
	'间断点': [],
	'连续性': [],
	'渐近线': [],
	'高阶导数': [],
	'隐函数求导': [],
	'变限积分求导': [],
	'参数方程': [],
	'弧长公式': [],
	'曲率': [],
	'偏导数': [],
	'全微分': [],
	'方向导数': [],
	'函数极值': ['极大值', '极小值', '极值'],
	'拉格朗日乘子法': [],
	'罗尔定理': [],
	'拉格朗日中值定理': [],
	'柯西中值定理': [],
	'凑微分': [],
	'换元法': [],
	'分部积分': [],
	'广义积分': [],
	'数值积分': [],
	'广义坐标变换': [],
	'积分中值定理': [],
	'技巧型积分': [],
	'奇偶对称性': [],
	'轮换对称性': [],
	'去绝对值': [],
	'几何意义': [],
	'交换积分次序': [],
	'积分区间': ['积分上下限'],
	'极坐标系积分': ['极坐标系'],
	'柱坐标系积分': [],
	'球坐标系积分': [],
	'广义坐标系积分': [],
	'截面法': [],
	'投影法': [],
	'不定积分': [],
	'三重积分': [],
	'第一类曲线积分': [],
	'第二类曲线积分': [],
	'第一类曲面积分': ['面积积分', '曲面面积'],
	'第二类曲面积分': ['坐标积分', '对坐标的积分'],
	'格林公式': [],
	'高斯公式': [],
	'斯托克斯公式': [],
	'定积分应用': ['体积', '质心', '转动惯量', '引力', '压力', '做功'],
	'定积分估值': [],
	'定积分定义': [],
	'摆线': [],
	'体积': [],
	'质心': [],
	'转动惯量': [],
	'引力': [],
	'做功': [],
	'矢量代数': [],
	'切法向量': [],
	'平面方程': [],
	'直线方程': [],
	'曲面方程': [],
	'点线面距离': ['距离'],
	'点线面投影': ['的投影'],
	'数项级数': [],
	'级数展开': [],
	'和函数': [],
	'敛散性': [],
	'收敛半径': [],
	'分离变量法': [],
	'一阶线性微分方程': [],
	'二阶线性微分方程': [],
	'matlab': ['MATLAB', 'Matlab']
}


def tag_posts():
	'''tag posts with pre-defined keywords'''
	for fname in os.listdir(source_posts):
		file_path = os.path.join(source_posts, fname)

		# get text
		with open(file_path, 'r', encoding='utf-8') as f:
			text = f.read()

		# check keywords
		tags = []		
		for k,v in keywords.items():
			find = True
			if not k in text:
				for vol in v:
					if vol in text:
						break
				else:
					find = False
			if find:
				tags.append(k)

		# write text		
		print(fname, ' with tags: ', tags if tags else 'UNTAGGED')

		if not tags:
			continue
		text = text.replace('tags  : UNTAGGED', 'tags  : {0}'.format(' '.join(tags)))
		with open(file_path, 'w', encoding='utf-8') as f:
			f.write(text)



def move_posts():
	'''move posts'''
	posts_ids = []
	for fname in os.listdir(source_posts):
		posts_ids.append(os.path.splitext(fname)[0].split('-')[-1])
		shutil.move(os.path.join(source_posts, fname), os.path.join(dest_posts, fname))
	return posts_ids


def move_images(posts_ids):
	'''move or remove images'''
	num_move, num_remove = 0, 0
	for fname in os.listdir(source_images):
		image_id = os.path.splitext(fname)[0].split('-')[1]
		if image_id in posts_ids:
			shutil.move(os.path.join(source_images, fname), os.path.join(dest_images, fname))
			num_move += 1
		else:
			os.remove(os.path.join(source_images, fname))
			num_remove += 1
	return num_move, num_remove

if __name__ == '__main__':

	print('Add tags according to keywords list...')
	print('-'*30)
	tag_posts()
	
	print('\nCopying posts and images to destination directories...')
	# move all posts
	posts_ids = move_posts()
	# move associated images
	m,n = move_images(posts_ids)

	# summary
	print('-'*30)
	print('{0} posts are moved.'.format(len(posts_ids)))
	print('{0} associated images are moved.'.format(m))
	print('{0} unused images are deleted.'.format(n))