#!/usr/bin/env python3
"""
移除 Xcode 项目中的所有 CocoaPods 引用
"""

import re
import sys

project_file = '/Users/apple/Desktop/PeakState/frontend/ios/App/App.xcodeproj/project.pbxproj'

print("🔧 移除 Xcode 项目中的 CocoaPods 引用...")

# 读取项目文件
with open(project_file, 'r') as f:
    content = f.read()

original_content = content

# 1. 移除 baseConfigurationReference
print("   - 移除配置文件引用...")
content = re.sub(r'\s*baseConfigurationReference = [A-F0-9]+ /\* Pods-.*?\.xcconfig \*/;', '', content)

# 2. 移除 Pods 框架引用
print("   - 移除框架引用...")
content = re.sub(r'\s*[A-F0-9]+ /\* Pods_App\.framework in Frameworks \*/ = \{isa = PBXBuildFile; fileRef = [A-F0-9]+ /\* Pods_App\.framework \*/; \};', '', content)

# 3. 移除 Pods 文件引用
print("   - 移除文件引用...")
content = re.sub(r'\s*[A-F0-9]+ /\* Pods_App\.framework \*/ = \{isa = PBXFileReference;.*?\};', '', content)
content = re.sub(r'\s*[A-F0-9]+ /\* Pods-App\.debug\.xcconfig \*/ = \{isa = PBXFileReference;.*?\};', '', content)
content = re.sub(r'\s*[A-F0-9]+ /\* Pods-App\.release\.xcconfig \*/ = \{isa = PBXFileReference;.*?\};', '', content)

# 4. 移除 Pods 组
print("   - 移除 Pods 组...")
# 找到并移除 Pods 组定义
pods_group_pattern = r'[A-F0-9]+ /\* Pods \*/ = \{[^}]*children = \([^)]*\);[^}]*\};'
content = re.sub(pods_group_pattern, '', content)

# 移除对 Pods 组的引用
content = re.sub(r',?\s*[A-F0-9]+ /\* Pods \*/,?', '', content)

# 5. 移除 Frameworks 组中的 Pods 框架
content = re.sub(r',?\s*[A-F0-9]+ /\* Pods_App\.framework \*/,?', '', content)

# 6. 清理空行
content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

# 保存修改后的文件
if content != original_content:
    with open(project_file, 'w') as f:
        f.write(content)
    print("✅ 成功移除 CocoaPods 引用")
else:
    print("ℹ️  没有找到需要移除的引用")

print("\n🎯 请在 Xcode 中：")
print("1. 关闭 Xcode")
print("2. 重新打开项目")
print("3. Product → Clean Build Folder")
print("4. 尝试构建")
