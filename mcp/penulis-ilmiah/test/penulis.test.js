import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { cekBaku } from '../dist/tools/cek_baku.js';
import { cekEjaan } from '../dist/tools/cek_ejaan.js';

describe('penulis-ilmiah MCP tools', () => {
  test('cekBaku identifies common non-standard Indonesian words', async () => {
    const input = {
      teks: 'Peneliti melakukan analisa data dan praktek lapangan untuk merubah hasil.',
      fallback_kbbi: false,
      max_lookup: 5
    };

    const res = await cekBaku(input);
    assert.equal(typeof res.ok, 'boolean');
    assert.ok(res.temuan.length >= 2, `Expected at least 2 findings, got ${res.temuan.length}`);
    
    const temuanWords = res.temuan.map(t => t.kata.toLowerCase());
    assert.ok(temuanWords.some(w => w.includes('analisa') || w.includes('praktek') || w.includes('merubah')), 'Should detect non-standard word');
  });

  test('cekEjaan flags affixed vs preposition "di"', async () => {
    const input = {
      teks: 'Sampel dikantor di uji dengan teliti.',
      pakai_hunspell: false
    };

    const res = await cekEjaan(input);
    assert.equal(typeof res.ok, 'boolean');
    assert.ok(res.ringkas.jumlah_temuan >= 1, `Expected at least 1 finding, got ${res.ringkas.jumlah_temuan}`);
    
    // Check for "dikantor" -> should suggest "di kantor"
    const hasPrepositionError = res.temuan.some(t => t.span.cuplikan.toLowerCase() === 'dikantor');
    assert.ok(hasPrepositionError, 'Should flag "dikantor" as error needing space');
  });

  test('cekEjaan accepts clean scholarly Indonesian text', async () => {
    const input = {
      teks: 'Penelitian ini dilakukan di laboratorium dengan mengamati perubahan nilai.',
      pakai_hunspell: false
    };

    const res = await cekEjaan(input);
    assert.equal(res.ok, true);
    assert.equal(res.ringkas.jumlah_temuan, 0, `Expected 0 findings for clean text, got ${res.ringkas.jumlah_temuan}`);
  });
});
