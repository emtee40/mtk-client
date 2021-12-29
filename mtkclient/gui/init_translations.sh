pyside2-lupdate main_gui.ui -ts tmp.ts
cat tmp.ts > i18n/de_DE.ts
cat tmp.ts > i18n/en_GB.ts
pyside2-lupdate readpart_gui.ui -ts tmp.ts
cat tmp.ts >> i18n/de_DE.ts
cat tmp.ts >> i18n/en_GB.ts
pyside2-lupdate readfull_gui.ui -ts tmp.ts
cat tmp.ts >> i18n/de_DE.ts
cat tmp.ts >> i18n/en_GB.ts
rm tmp.ts

