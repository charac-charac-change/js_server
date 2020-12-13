import pretrained_networks
import os
import sys
import shutil
import bz2
from tensorflow.keras.utils import get_file
from ffhq_dataset.face_alignment import image_align
from ffhq_dataset.landmarks_detector import LandmarksDetector
from align_images import unpack_bz2
from project_images import project_image
import projector
print(os.getcwd())
# use my copy of the blended model to save Doron's download bandwidth
# get the original here https://mega.nz/folder/OtllzJwa#C947mCCdEfMCRTWnDcs4qw
blended_url = "stylegan2/ffhq-cartoon-blended-64.pkl"
ffhq_url = "stylegan2/stylegan2-ffhq-config-f.pkl"
LANDMARKS_MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'

_, _, Gs_blended = pretrained_networks.load_networks(blended_url)
_, _, Gs = pretrained_networks.load_networks(ffhq_url)
#end of pretrained_networks

landmarks_model_path = unpack_bz2(get_file('shape_predictor_68_face_landmarks.dat.bz2',
                                               LANDMARKS_MODEL_URL, cache_subdir='temp'))

def inference():
  RAW_IMAGES_DIR = 'stylegan2/raw'
  ALIGNED_IMAGES_DIR = 'stylegan2/aligned'

  landmarks_detector = LandmarksDetector(landmarks_model_path)
  for img_name in [x for x in os.listdir(RAW_IMAGES_DIR) if x[0] not in '._']:
      raw_img_path = os.path.join(RAW_IMAGES_DIR, img_name)
      for i, face_landmarks in enumerate(landmarks_detector.get_landmarks(raw_img_path), start=1):
          face_img_name = '%s_%02d.png' % (os.path.splitext(img_name)[0], i)
          aligned_face_path = os.path.join(ALIGNED_IMAGES_DIR, face_img_name)
          os.makedirs(ALIGNED_IMAGES_DIR, exist_ok=True)
          image_align(raw_img_path, aligned_face_path, face_landmarks)
  # end of align_images

  network_pkl = 'http://d36zk2xti64re0.cloudfront.net/stylegan2/networks/stylegan2-ffhq-config-f.pkl'
  vgg16_pkl = 'http://d36zk2xti64re0.cloudfront.net/stylegan1/networks/metrics/vgg16_zhang_perceptual.pkl'
  num_steps = 100
  initial_learning_rate = 0.1
  initial_noise_factor = 0.05
  verbose = False
  src_dir = ALIGNED_IMAGES_DIR
  dst_dir = 'stylegan2/generated'
  tmp_dir = 'stylegan2/stylegan2-tmp'
  video = False
  print('Loading networks from "%s"...' % network_pkl)
  _G, _D, Gs = pretrained_networks.load_networks(network_pkl)
  proj = projector.Projector(
      vgg16_pkl             = vgg16_pkl,
      num_steps             = num_steps,
      initial_learning_rate = initial_learning_rate,
      initial_noise_factor  = initial_noise_factor,
      verbose               = verbose
  )
  proj.set_network(Gs)

  src_files = sorted([os.path.join(src_dir, f) for f in os.listdir(src_dir) if f[0] not in '._'])
  print(src_files)  
  for src_file in src_files:
      project_image(proj, src_file, dst_dir, tmp_dir, video=video)
      if video:
          render_video(
              src_file, args.dst_dir, args.tmp_dir, args.num_steps, args.video_mode,
              args.video_size, args.video_fps, args.video_codec, args.video_bitrate
          )
      shutil.rmtree(tmp_dir)

