# 推送代码到GitHub

## 步骤

1. 打开终端，进入项目目录：
```bash
cd ~/.openclaw/workspace/docparser-pro/web-free
```

2. 配置GitHub用户名（如果还没配置）：
```bash
git config user.name "binziai7996"
git config user.email "binziai7996@gmail.com"
```

3. 推送到GitHub：
```bash
git push -u origin master
```

4. 输入GitHub用户名和密码/Token

## 如果遇到问题

### 问题1：需要Token而不是密码
GitHub现在需要Personal Access Token代替密码：
1. 打开 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 "repo" 权限
4. 生成Token并复制
5. 推送时用这个Token代替密码

### 问题2：网络超时
多试几次，或者使用手机热点

## 推送成功后

告诉我，我会继续部署到Render！
