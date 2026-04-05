const contactMessages = {
  {% for contact in contacts %}
  "{{ contact.name }}": {
    av: "{{ contact.avatar_class }}",
    initials: "{{ contact.initials }}",
    status: "{{ contact.status }}",
    messages: [
      {% set ns = namespace(msgs=[]) %}
      {% for d in messages_ %}{% if contact.name in d %}{% set ns.msgs = d[contact.name] %}{% endif %}{% endfor %}
      {% for msg in ns.msgs %}{% if msg.role != "system" %}{
        type: "{{ 'in' if msg.role == 'assistant' else 'out' }}",
        text: {{ msg.content | tojson }},
        time: "{{ msg.time | default('') }}",
        code: null
      }{% if not loop.last %},{% endif %}{% endif %}{% endfor %}
    ]
  }{% if not loop.last %},{% endif %}
  {% endfor %}
};
const contactInfo = {{ contact_info | tojson }};