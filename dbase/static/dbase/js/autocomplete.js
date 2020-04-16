import $ from 'jquery';

import Bloodhound from 'corejs-typeahead/dist/bloodhound.js';
import 'corejs-typeahead/dist/typeahead.jquery.js';


/*global materialsUrl, materialAliasesUrl */
export const materialEngine = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  prefetch: materialsUrl,
});

export const materialaliasEngine = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  prefetch: materialAliasesUrl,
});

export default class Autocomplete {

  constructor($elem) {

    this._$elem = $elem;
    this._allowCustomMaterial = $elem.data('allowcustom');
    this._selected = {
      id: $elem.data('materialid'),
      name: $elem.data('materialname')
    };
    this._initial = this._selected;
    if (this._initial.id === '') {
      this.invalidate();
    }

    this._setup();
  }

  get selectedItem() {
    return this._selected;
  }

  invalidate() {
    this._$elem.get(0).setCustomValidity(this._$elem.data('invalidmessage') || 'invalid');
  }

  validate() {
    this._$elem.get(0).setCustomValidity('');
  }

  set selectedItem(obj) {
    this._selected = obj;
    this._$elem.typeahead('val', obj.name);
  }

  reset() {
    this._selected = this._initial;
    if (this._initial.name !== undefined) {
      this._$elem.typeahead('val', this._initial.name);
    } else {
      this._$elem.typeahead('val', '');
    }
    if (this._selected.id === '') {
      this.invalidate();
    } else {
      this.validate();
    }
  }

  _setup() {
    this._$elem.typeahead(
      {
        hint: true,
        highlight: true,
        minLength: 1,
        autoselect: true,
      }, {
        name: 'materials',
        source: materialEngine,
        display: 'name',
        templates: {
          suggestion: e => {
            let imgHtml;
            if (e.images.length > 0) {
              imgHtml = `<div class="tt-suggestion-image float-right"><img src="${e.images[0]}"></div>`;
            } else {
              imgHtml = '<div class="tt-suggestion-image tt-suggestion-no-image"></div>';
            }
            return `<div class="clearfix">
                        ${imgHtml}
                        <div class="tt-suggestion-text">
                            <div class="tt-suggestion-name" data-id="${e.id}">${e.name}</div>
                            <div class="clearfix">
                                <div class="tt-suggestion-category">${(e.categories.length > 0 ? e.categories[0] : '')}</div>
                                ${(e.gm === true ? '<div class="tt-suggestion-gm">GM</div>' : '')}
                            </div>
                        </div>
                    </div>`;
          },
          empty: e => {
            if (this._allowCustomMaterial) {
              const $empty =
                $(`<div class="clearfix tt-suggestion tt-selectable">
                      <div class="tt-suggestion-name">${this._$elem.data('notfoundtext')}</div>
                      <div class="clearfix">
                          <div class="tt-suggestion-category">${this._$elem.data('addcustomtext').replace('{}', e.query)}</div>
                      </div>
                    </div>`);
              $empty.click(_ => {
                this.selectedItem = {
                  id: e.query,
                  name: e.query
                };
                this.validate();
                this._$elem.typeahead('close');
              });

              return $empty;
            } else {
              return `<div class="clearfix tt-suggestion">
                        <div class="tt-suggestion-name">${this._$elem.data('notfoundtext')}</div>
                      </div>`;
            }
          }
        }
      }, {
        name: 'materialaliases',
        source: materialaliasEngine,
        display: 'name',
        templates: {
          suggestion: e => {
            let imgHtml;
            if (e.material.images.length > 0) {
              imgHtml = `<div class="tt-suggestion-image float-right"><img src="${e.material.images[0]}"></div>`;
            } else {
              imgHtml = '<div class="tt-suggestion-image tt-suggestion-no-image"></div>';
            }
            return `<div class="clearfix">
                        ${imgHtml}
                        <div class="tt-suggestion-text">
                            <div class="tt-suggestion-name" data-id="${e.material.id}">${e.name}</div>
                            <div class="tt-suggestion-alias">${e.material.name}</div>
                            <div class="clearfix">
                                <div class="tt-suggestion-category">${(e.material.categories.length > 0 ? e.material.categories[0] : '')}</div>
                                ${(e.material.gm === true ? '<div class="tt-suggestion-gm">GM</div>' : '')}
                            </div>
                        </div>
                    </div>`;
          }
        }
      }
    );
    this._$elem.bind('typeahead:select', (ev, suggestion) => {
      if (suggestion.material !== undefined) {
        suggestion = suggestion.material;
        this._$elem.typeahead('val', suggestion.name);
      }
      this._selected = suggestion;
      this.validate();
    });
  }

  static getAutocomplete($elem) {
    if ($elem.length > 1) {
      $elem = $elem.first();
    }
    let $typeahead = $elem.closest('span.twitter-typeahead');
    if ($typeahead.length > 0) {
      return $typeahead.data('autocomplete');
    } else {
      const ac = new Autocomplete($elem);
      // The $typeahead span is constructed by Autocomplete()
      $typeahead = $elem.closest('span.twitter-typeahead');
      $typeahead.data('autocomplete', ac);
      return ac;
    }
  }
}

$('.typeahead-materials').each((i, elem) => {
  Autocomplete.getAutocomplete($(elem));
});
