import re
from datetime import datetime
from pathlib import Path
import argparse
from multiprocessing import Pool, cpu_count

def convert_pns_to_makimaru(input_file, output_file):
    # pnsのヘッダーフィールドを格納する辞書
    header_pns = {}
    content = []
    in_header = False
    header_end_marker = "============================="

    # ファイル読み込みとヘッダー解析
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == header_end_marker:
                break
            if not in_header and "Saved by pixiv-novel-saver" in line:
                in_header = True
            if in_header:
                if ':' in line:
                    key, value = line.split(':', 1)
                    header_pns[key.strip()] = value.strip()
            else:
                content.append(line)
        # 残りのコンテンツを取得
        content += f.readlines()

    # 巻丸のヘッダー生成
    header_makimaru = []
    header_makimaru.append(f"TITLE: {header_pns.get('title', '')}")
    header_makimaru.append(f"SERIES: {header_pns.get('series', '')}")
    header_makimaru.append(f"AUTHOR: {header_pns.get('author', '')}")
    header_makimaru.append("SITE: pixiv")
    header_makimaru.append(f"URL: https://www.pixiv.net/novel/show.php?id={header_pns.get('id', '')}")
    header_makimaru.append("PREV: ")
    header_makimaru.append("NEXT: ")
    header_makimaru.append("M----------------------------------------M")
    
    # 説明文の処理
    if 'description' in header_pns:
        description = header_pns['description'].replace('<br />', '\n')
        header_makimaru.append(description)
    
    header_makimaru.append("--------------------")

    # ファイル書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(header_makimaru))
        f.write('\n')
        f.write(''.join(content))

def process_file(input_file):
    output_file = input_file.with_stem(f"{input_file.stem}-converted")
    convert_pns_to_makimaru(str(input_file), str(output_file))
    print(f"変換完了: {input_file} → {output_file}")

def main():
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='pns → 巻丸 ヘッダー変換ツール')
    parser.add_argument('input', nargs='+', help='入力ファイル名（複数指定可）')
    parser.add_argument('-f', '--force', action='store_true', help='出力ファイルを上書きする')
    
    args = parser.parse_args()
    
    # 入力ファイルのリストを取得
    input_files = [Path(file) for file in args.input]
    
    # 並列処理
    with Pool(cpu_count()) as pool:
        pool.map(process_file, input_files)

if __name__ == '__main__':
    main()