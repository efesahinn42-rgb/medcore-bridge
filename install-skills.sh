#!/bin/bash
# Yeni projeye geçince bu scripti çalıştır:
# bash ~/Desktop/NextJS-Starter-Kit/install-skills.sh

echo "📦 Skill paketleri kuruluyor..."

npx skills@latest add mattpocock/skills
npx skills@latest add DietrichGebert/ponytail
npx skills@latest add obra/superpowers
npx skills@latest add https://github.com/greensock/gsap-skills

echo "✅ Tüm skill paketleri kuruldu."
echo ""
echo "📋 Yapılacaklar:"
echo "  1. settings.json → ~/.claude/settings.json üzerine kopyala (MCP'leri birleştir)"
echo "  2. CLAUDE.md → projenin kök dizinine kopyala ve düzenle"
echo "  3. GitHub token'ı settings.json'daki YOUR_TOKEN_HERE ile değiştir"
echo "  4. codebase-memory-mcp zaten kurulu — 'index_repository' ile indeksle"
