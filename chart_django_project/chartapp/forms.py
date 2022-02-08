from django import forms


class ChartForm(forms.Form):
    chart = forms.ChoiceField(choices=[('pie', 'Pie Chart'), ('line', 'Linear Chart'), ('bar', 'Bar Chart')])