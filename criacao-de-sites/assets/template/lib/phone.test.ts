import { test } from 'node:test'
import assert from 'node:assert/strict'
import { DDD_REGEX, formatMobile, isValidMobile, toDigits, toInternational } from './phone.ts'

test('67 DDDs válidos', () => {
  let n = 0
  for (let i = 10; i <= 99; i += 1) if (DDD_REGEX.test(String(i))) n += 1
  assert.equal(n, 67)
})

test('normaliza +55, 55, 0 e pontuação', () => {
  assert.equal(toDigits('+55 (11) 91234-5678'), '11912345678')
  assert.equal(toDigits('55 11 91234 5678'), '11912345678')
  assert.equal(toDigits('011 91234-5678'), '11912345678')
  assert.equal(toDigits('(11) 91234-5678'), '11912345678')
})

test('DDD 55 não é confundido com o código do país', () => {
  assert.equal(toDigits('55 99123-4567'), '55991234567')
  assert.equal(isValidMobile('55991234567'), true)
})

test('validação de celular', () => {
  assert.equal(isValidMobile('11912345678'), true)
  assert.equal(isValidMobile('1191234567'), false) // 10 dígitos (fixo)
  assert.equal(isValidMobile('20912345678'), false) // DDD 20 não existe
  assert.equal(isValidMobile('11812345678'), false) // sem o 9
})

test('formatação', () => {
  assert.equal(formatMobile('11912345678'), '(11) 91234-5678')
  assert.equal(formatMobile('1191'), '(11) 91')
  assert.equal(toInternational('11912345678'), '5511912345678')
})
