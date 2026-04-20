# 航空運賃・空港使用料検索

このフォルダには、ANA/JALの運賃表PDFと空港使用料表をもとにした静的Webサイトがあります。

## 公開用ファイル

ネット公開するときは、`site` フォルダの中身をそのままホスティングサービスへ配置します。

- `site/index.html`
- `site/app-data.js`
- `site/.nojekyll`

## 公開用ファイルの更新

運賃PDFを差し替えたあと、PowerShellでこのフォルダを開いて次を実行します。

```powershell
.\publish-site.ps1
```

別のPDFを指定する場合は次です。

```powershell
.\publish-site.ps1 -FarePdf "C:\path\to\新しい料金表.pdf"
```

## 公開方法

### 1. Netlify

いちばん簡単です。`site` フォルダをNetlifyへドラッグ＆ドロップするだけで公開できます。

### 2. GitHub Pages

このフォルダには GitHub Pages 用のワークフローが入っています。
リポジトリを GitHub に push して `main` ブランチへ反映すると、`site` フォルダが自動で公開されます。

基本手順:

1. GitHubで新しいリポジトリを作成します。
2. このフォルダ一式をそのリポジトリへ push します。
3. GitHub の `Settings > Pages` を開きます。
4. `Build and deployment` の `Source` を `GitHub Actions` にします。
5. `main` に push すると公開されます。

公開URLの例:

`https://ユーザー名.github.io/リポジトリ名/`

### 3. 社内サーバー / SharePoint / 認証付きWeb環境

社外公開したくない場合は、`site` フォルダの中身を社内限定のWeb公開先へ配置してください。

## ファイル構成

- `index.html`: 画面本体
- `build_data.py`: 運賃PDFから `app-data.js` を生成
- `publish-site.ps1`: 公開用 `site` フォルダを作成・更新
- `update-fares.ps1`: ルートの `app-data.js` を更新

## 補足

- 運賃はPDFから抽出した最安値を路線単位で保持しています。
- 空港使用料は現在コード内の表データを利用しています。
- 東京や大阪のような複数空港エリアは、画面上で空港を選べます。
