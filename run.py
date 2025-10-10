#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译API项目运行脚本
支持Windows、Linux和macOS系统

功能：
- 环境检查和依赖安装
- 环境变量配置检查
- 启动FastAPI应用
- 运行测试
- 构建文档
- 清理缓存
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
import shutil
import time

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv 未安装，.env文件不会被自动加载")
    print("请运行: pip install python-dotenv")

class ProjectRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.is_windows = platform.system() == "Windows"
        self.python_cmd = "python" if self.is_windows else "python3"
        self.pip_cmd = "pip"

    def run_command(self, command, cwd=None, shell=True):
        """运行命令并返回结果"""
        try:
            print(f"执行命令: {command}")
            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8' if self.is_windows else None
            )
            if result.returncode != 0:
                print(f"命令执行失败: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"命令执行异常: {e}")
            return False

    def check_python_version(self):
        """检查Python版本"""
        print("检查Python版本...")
        try:
            result = subprocess.run([self.python_cmd, "--version"],
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"✓ {version}")
            return True
        except Exception as e:
            print(f"✗ Python检查失败: {e}")
            return False

    def check_dependencies(self):
        """检查并安装依赖"""
        print("\n检查项目依赖...")

        # 检查requirements.txt是否存在
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            print("✗ requirements.txt文件不存在")
            return False

        # 尝试安装依赖
        print("安装项目依赖...")
        if not self.run_command(f"{self.pip_cmd} install -r requirements.txt"):
            print("✗ 依赖安装失败")
            return False

        print("✓ 依赖安装完成")
        return True

    def check_env_file(self):
        """检查环境变量配置"""
        print("\n检查环境配置...")

        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_example.exists():
            print("✗ .env.example文件不存在")
            return False

        if not env_file.exists():
            print("⚠ .env文件不存在，从.env.example复制...")
            try:
                shutil.copy(env_example, env_file)
                print("✓ 已创建.env文件，请编辑其中的API密钥")
                print("重要提示：请在.env文件中配置AI模型的API密钥")
                return False  # 需要用户配置
            except Exception as e:
                print(f"✗ 复制.env文件失败: {e}")
                return False

        # 重新加载环境变量以确保 .env 文件中的变量被加载
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file, override=True)
        except ImportError:
            print("⚠ python-dotenv 未安装，无法加载 .env 文件")

        # 检查必要的环境变量
        required_vars = [
            'OPENAI_API_KEY',
            'ZHIPUAI_API_KEY',
            'DASHSCOPE_API_KEY'
        ]

        missing_vars = []
        placeholder_values = [
            'your_openai_api_key_here',
            'your_zhipuai_api_key_here',
            'your_dashscope_api_key_here'
        ]

        for var in required_vars:
            value = os.getenv(var)
            if not value or value.strip() == '' or value in placeholder_values:
                missing_vars.append(var)

        if missing_vars:
            print(f"⚠ 缺少必要的环境变量或使用默认占位符: {', '.join(missing_vars)}")
            print("请在.env文件中配置真实的API密钥")
            print("例如:")
            print("  OPENAI_API_KEY=sk-your-actual-openai-key")
            print("  ZHIPUAI_API_KEY=your-actual-zhipu-key")
            print("  DASHSCOPE_API_KEY=your-actual-dashscope-key")
            return False

        print("✓ 环境配置检查完成")
        return True

    def start_app(self, host="127.0.0.1", port=8000, reload=True):
        """启动FastAPI应用"""
        print(f"\n启动FastAPI应用 (host={host}, port={port})...")

        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)

        # 构建命令
        cmd = [
            self.python_cmd, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port)
        ]

        if reload:
            cmd.append("--reload")

        print(f"启动命令: {' '.join(cmd)}")
        print("应用正在启动...")
        print(f"API文档地址: http://{host}:{port}/docs")
        print("按Ctrl+C停止服务")

        try:
            subprocess.run(cmd, cwd=self.project_root, env=env)
        except KeyboardInterrupt:
            print("\n应用已停止")
        except Exception as e:
            print(f"启动失败: {e}")

    def run_tests(self, verbose=False):
        """运行测试"""
        print("\n运行测试...")

        cmd = [self.python_cmd, "-m", "pytest", "tests/"]
        if verbose:
            cmd.extend(["-v", "--tb=short"])

        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)

        try:
            result = subprocess.run(cmd, cwd=self.project_root, env=env)
            return result.returncode == 0
        except Exception as e:
            print(f"测试运行失败: {e}")
            return False

    def build_docs(self):
        """构建文档"""
        print("\n构建文档...")

        if not (self.project_root / "mkdocs.yml").exists():
            print("⚠ mkdocs.yml不存在，跳过文档构建")
            return True

        cmd = [self.python_cmd, "-m", "mkdocs", "build"]
        return self.run_command(cmd)

    def clean_cache(self):
        """清理缓存文件"""
        print("\n清理缓存文件...")

        cache_dirs = [
            "__pycache__",
            ".pytest_cache",
            "*.pyc",
            "*.pyo",
            "*.pyd"
        ]

        cleaned = 0
        for pattern in cache_dirs:
            if pattern.endswith("/"):
                # 目录模式
                for path in self.project_root.rglob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned += 1
            else:
                # 文件模式
                for path in self.project_root.rglob(pattern):
                    if path.is_file():
                        path.unlink(missing_ok=True)
                        cleaned += 1

        print(f"✓ 已清理 {cleaned} 个缓存文件/目录")
        return True

    def show_help(self):
        """显示帮助信息"""
        help_text = """
翻译API项目运行脚本

使用方法:
  python run.py [command] [options]

可用命令:
  check      检查环境和依赖
  install    安装项目依赖
  env        检查环境变量配置
  start      启动FastAPI应用
  test       运行测试
  docs       构建文档
  clean      清理缓存文件
  all        执行完整流程 (check -> install -> env -> start)

选项:
  --host HOST       服务器主机地址 (默认: 127.0.0.1)
  --port PORT       服务器端口 (默认: 8000)
  --no-reload       启动时不启用自动重载
  --verbose         测试时显示详细输出

示例:
  python run.py start                    # 启动应用
  python run.py test --verbose           # 运行详细测试
  python run.py start --host 0.0.0.0     # 在所有接口上启动
  python run.py all                      # 执行完整流程
        """
        print(help_text)

def main():
    parser = argparse.ArgumentParser(description="翻译API项目运行脚本")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["check", "install", "env", "start", "test", "docs", "clean", "all", "help"])
    parser.add_argument("--host", default="127.0.0.1", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--no-reload", action="store_true", help="启动时不启用自动重载")
    parser.add_argument("--verbose", action="store_true", help="测试时显示详细输出")

    args = parser.parse_args()

    runner = ProjectRunner()

    if args.command == "help":
        runner.show_help()
        return

    # 执行相应命令
    if args.command == "check":
        success = runner.check_python_version()
        if success:
            print("✓ 环境检查完成")

    elif args.command == "install":
        success = runner.check_dependencies()

    elif args.command == "env":
        success = runner.check_env_file()

    elif args.command == "start":
        if not runner.check_env_file():
            print("请先配置环境变量")
            return
        runner.start_app(args.host, args.port, not args.no_reload)

    elif args.command == "test":
        if not runner.check_env_file():
            print("请先配置环境变量")
            return
        success = runner.run_tests(args.verbose)

    elif args.command == "docs":
        success = runner.build_docs()

    elif args.command == "clean":
        success = runner.clean_cache()

    elif args.command == "all":
        print("执行完整项目流程...")

        # 1. 环境检查
        if not runner.check_python_version():
            return

        # 2. 安装依赖
        if not runner.check_dependencies():
            return

        # 3. 检查环境配置
        if not runner.check_env_file():
            return

        # 4. 运行测试
        if not runner.run_tests():
            print("⚠ 测试失败，但继续启动应用")
            time.sleep(2)

        # 5. 构建文档
        runner.build_docs()

        # 6. 启动应用
        print("\n" + "="*50)
        print("所有检查完成，开始启动应用...")
        runner.start_app(args.host, args.port, not args.no_reload)

if __name__ == "__main__":
    main()