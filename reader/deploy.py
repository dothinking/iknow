import os
import shutil

# source and desination folder
source_posts = os.path.join(os.getcwd(), '_posts')
source_images = os.path.join(os.getcwd(), '_images')
dest_posts = 'D:\\website\\iknow\\_posts'
dest_images = 'D:\\website\\iknow\\public\\uploads'

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
	
	print('The destination directories for posts and images are:\n{0}\n{1}'.format(dest_posts, dest_images))
	go = input('Would you continue? Y/N\n')

	if not go.upper()=='Y': exit(0)

	# move all posts
	posts_ids = move_posts()

	# move associated images
	m,n = move_images(posts_ids)

	# summary
	print('---------------------------')
	print('{0} posts are moved.'.format(len(posts_ids)))
	print('{0} associated images are moved.'.format(m))
	print('{0} unused images are deleted.'.format(n))




