/**
 * Card Review Tracking — Writing Coaching Cards
 *
 * Sends review events to a Google Sheets endpoint so you can see
 * whether students reviewed their cards and how long they spent.
 *
 * EVENTS TRACKED:
 *   opened           — student loaded the page
 *   card_view        — time spent on each card (sent when they navigate away)
 *   discrim_correct  — discrimination challenge completed correctly
 *   checklist_done   — all checklist items checked
 *   completed        — reached the completion celebration overlay
 *
 * ═══════════════════════════════════════════════════════════════════
 * SETUP — ONE-TIME (takes ~5 minutes)
 * ═══════════════════════════════════════════════════════════════════
 *
 * 1. Create a new Google Sheet (or use an existing one)
 *
 * 2. Go to  Extensions > Apps Script
 *
 * 3. Delete any code in the editor, then paste this entire block:
 *
 *    ┌──────────────────────────────────────────────────────────┐
 *    │  function doGet(e)  { return handleRequest(e); }        │
 *    │  function doPost(e) { return handleRequest(e); }        │
 *    │                                                          │
 *    │  function handleRequest(e) {                             │
 *    │    var ss = SpreadsheetApp.getActiveSpreadsheet();       │
 *    │    var sheet = ss.getSheetByName('Card Reviews');        │
 *    │    if (!sheet) {                                         │
 *    │      sheet = ss.insertSheet('Card Reviews');             │
 *    │      sheet.appendRow([                                   │
 *    │        'Timestamp', 'Session', 'Student',                │
 *    │        'Card File', 'Event', 'Card #',                  │
 *    │        'Card Title', 'Time on Card (s)', 'Detail'       │
 *    │      ]);                                                 │
 *    │      sheet.getRange(1,1,1,9).setFontWeight('bold');     │
 *    │      sheet.setFrozenRows(1);                             │
 *    │    }                                                     │
 *    │    var p = e.parameter || {};                             │
 *    │    sheet.appendRow([                                      │
 *    │      p.ts   || new Date().toISOString(),                 │
 *    │      p.sid  || '',                                       │
 *    │      p.stu  || '',                                       │
 *    │      p.file || '',                                       │
 *    │      p.evt  || '',                                       │
 *    │      p.card || '',                                       │
 *    │      p.title|| '',                                       │
 *    │      p.time || '',                                       │
 *    │      p.det  || ''                                        │
 *    │    ]);                                                    │
 *    │    return ContentService.createTextOutput('ok');          │
 *    │  }                                                       │
 *    └──────────────────────────────────────────────────────────┘
 *
 * 4. Click  Deploy > New Deployment
 *    - Click the gear icon and select "Web app"
 *    - Set "Execute as" to "Me"
 *    - Set "Who has access" to "Anyone"
 *    - Click Deploy
 *    - Authorize when prompted (click through the "unsafe" warning)
 *
 * 5. Copy the Web App URL (looks like https://script.google.com/macros/s/.../exec)
 *
 * 6. Paste it into the ENDPOINT variable below
 *
 * 7. Commit and push — tracking is now live
 *
 * ═══════════════════════════════════════════════════════════════════
 */

(function() {
  // ═══ PASTE YOUR GOOGLE APPS SCRIPT WEB APP URL HERE ═══
  var ENDPOINT = '';

  // If no endpoint configured, tracking is silently disabled
  if (!ENDPOINT) return;

  // ── Session state ──
  var sid = Date.now().toString(36) + Math.random().toString(36).substr(2, 4);
  var pageLoad = Date.now();
  var student, file;
  var activeIdx = -1;
  var cardStart = Date.now();
  var deduped = {};

  // ── Helpers ──
  function encode(obj) {
    var parts = [];
    for (var k in obj) {
      if (obj.hasOwnProperty(k) && obj[k] !== '' && obj[k] != null) {
        parts.push(encodeURIComponent(k) + '=' + encodeURIComponent(obj[k]));
      }
    }
    return parts.join('&');
  }

  function send(evt, data, once) {
    if (once) {
      var key = evt + '|' + (data.card || '');
      if (deduped[key]) return;
      deduped[key] = true;
    }
    var payload = {
      ts: new Date().toISOString(),
      sid: sid,
      stu: student,
      file: file,
      evt: evt,
      card: data.card || '',
      title: data.title || '',
      time: data.time || '',
      det: data.detail || ''
    };
    new Image().src = ENDPOINT + '?' + encode(payload);
  }

  function beacon(evt, data) {
    var payload = {
      ts: new Date().toISOString(),
      sid: sid,
      stu: student,
      file: file,
      evt: evt,
      card: data.card || '',
      title: data.title || '',
      time: data.time || '',
      det: data.detail || ''
    };
    var url = ENDPOINT + '?' + encode(payload);
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url);
    } else {
      new Image().src = url;
    }
  }

  function getStudent() {
    var h2 = document.querySelector('.card-header h2');
    return h2 ? h2.textContent.trim() : 'Unknown';
  }

  function getFile() {
    var parts = window.location.pathname.split('/').filter(Boolean);
    for (var i = parts.length - 1; i >= 0; i--) {
      if (parts[i] !== 'index.html') return parts[i];
    }
    return document.title || 'Unknown';
  }

  function getActiveCard() {
    var cards = document.querySelectorAll('.card');
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].classList.contains('active')) return i;
    }
    return -1;
  }

  function getTitle(idx) {
    var cards = document.querySelectorAll('.card');
    return cards[idx] ? (cards[idx].getAttribute('data-title') || 'Card ' + (idx + 1)) : '';
  }

  // ── Initialize ──
  function init() {
    student = getStudent();
    file = getFile();
    activeIdx = getActiveCard();
    cardStart = Date.now();

    // 1. Opened
    send('opened', {
      card: activeIdx + 1,
      title: getTitle(activeIdx),
      detail: document.querySelectorAll('.card').length + ' cards'
    }, true);

    // 2. Poll for card navigation (every 500ms)
    setInterval(function() {
      var now = getActiveCard();
      if (now !== activeIdx && now >= 0) {
        var elapsed = Math.round((Date.now() - cardStart) / 1000);
        send('card_view', {
          card: activeIdx + 1,
          title: getTitle(activeIdx),
          time: elapsed
        }, false);
        activeIdx = now;
        cardStart = Date.now();
      }
    }, 500);

    // 3. Discrimination completions (event delegation)
    document.addEventListener('click', function(e) {
      var opt = e.target.closest ? e.target.closest('.discrim-option') : null;
      if (!opt) return;
      setTimeout(function() {
        if (opt.classList.contains('correct')) {
          var card = opt.closest('.card');
          var cards = document.querySelectorAll('.card');
          var idx = Array.prototype.indexOf.call(cards, card);
          send('discrim_correct', {
            card: idx + 1,
            title: getTitle(idx)
          }, true);
        }
      }, 200);
    });

    // 4. Checklist completion
    document.addEventListener('click', function(e) {
      var item = e.target.closest ? e.target.closest('.check-item') : null;
      if (!item) return;
      setTimeout(function() {
        var checked = document.querySelectorAll('.check-item.checked').length;
        var total = document.querySelectorAll('.check-item').length;
        if (total > 0 && checked === total) {
          send('checklist_done', {
            card: activeIdx + 1,
            detail: checked + '/' + total
          }, true);
        }
      }, 200);
    });

    // 5. Completion overlay
    var overlay = document.getElementById('completionOverlay');
    if (overlay) {
      new MutationObserver(function() {
        if (overlay.classList.contains('visible')) {
          var total = Math.round((Date.now() - pageLoad) / 1000);
          send('completed', {
            card: document.querySelectorAll('.card').length,
            detail: total + 's total'
          }, true);
        }
      }).observe(overlay, { attributes: true, attributeFilter: ['class'] });
    }

    // 6. Page unload — send final card time
    window.addEventListener('beforeunload', function() {
      var elapsed = Math.round((Date.now() - cardStart) / 1000);
      beacon('card_view', {
        card: activeIdx + 1,
        title: getTitle(activeIdx),
        time: elapsed,
        detail: 'final'
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
