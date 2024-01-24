from django import forms


class ItemCreateForm(forms.Form):
	board_id = forms.IntegerField()
	item_name = forms.CharField(max_length=200)
	status = forms.CharField(max_length=200)
	date = forms.DateField()


class SubitemCreateForm(forms.Form):
	item_id = forms.IntegerField()
	item_name = forms.CharField(max_length=200)
	status = forms.CharField(max_length=200)
	date = forms.DateField()


class ItemUpdateForm(forms.Form):
	board_id = forms.IntegerField()
	item_id = forms.IntegerField()
	item_name = forms.CharField(max_length=200)
	status = forms.CharField(max_length=200)
	date = forms.DateField()


class ItemDeleteForm(forms.Form):
	item_id = forms.IntegerField()
