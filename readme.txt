1.main.py检测
2.clear_result.py清除result文件夹里的检测结果
3.addition文件夹里的warp.py去掉背景后检测,最终版本为warp_v3.py。

warp 不能手动调节参数
warp_v2 先调节变换后的图像，再按‘a’进行检测，按‘b’回退进行手动调节
warp_v3 可直接在检测结果中拖动滑窗，调节参数