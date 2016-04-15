import os
import tempfile
import zipfile
# import autocomplete_light
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from django.forms.widgets import CheckboxSelectMultiple
from utils import unzip_file
# from geonode.layers.models import Layer, Attribute
# from project.models import Project

from django import forms


class JSONField(forms.CharField):

    def clean(self, text):
        text = super(JSONField, self).clean(text)
        try:
            return json.loads(text)
        except ValueError:
            raise forms.ValidationError("this field must be valid JSON")


class LayerUploadForm(forms.Form):
    base_file = forms.FileField()
    dbf_file = forms.FileField(required=False)
    shx_file = forms.FileField(required=False)
    prj_file = forms.FileField(required=False)
    xml_file = forms.FileField(required=False)

    charset = forms.CharField(required=False)

    spatial_files = (
        "base_file",
        "dbf_file",
        "shx_file",
        "prj_file")

    def clean(self):
        cleaned = super(LayerUploadForm, self).clean()
        dbf_file = shx_file = prj_file = xml_file = None
        base_name = base_ext = None
        if zipfile.is_zipfile(cleaned["base_file"]):
            filenames = zipfile.ZipFile(cleaned["base_file"]).namelist()
            for filename in filenames:
                name, ext = os.path.splitext(filename)
                if ext.lower() == '.shp':
                    if base_name is not None:
                        raise forms.ValidationError(
                            "Only one shapefile per zip is allowed")
                    base_name = name
                    base_ext = ext
                elif ext.lower() == '.dbf':
                    dbf_file = filename
                elif ext.lower() == '.shx':
                    shx_file = filename
                elif ext.lower() == '.prj':
                    prj_file = filename
                elif ext.lower() == '.xml':
                    xml_file = filename
            if base_name is None:
                raise forms.ValidationError(
                    "Zip files can only contain shapefile.")
        else:
            base_name, base_ext = os.path.splitext(cleaned["base_file"].name)
            if cleaned["dbf_file"] is not None:
                dbf_file = cleaned["dbf_file"].name
            if cleaned["shx_file"] is not None:
                shx_file = cleaned["shx_file"].name
            if cleaned["prj_file"] is not None:
                prj_file = cleaned["prj_file"].name
            if cleaned["xml_file"] is not None:
                xml_file = cleaned["xml_file"].name

        if base_ext.lower() not in (".shp", ".tif", ".tiff", ".geotif", ".geotiff"):
            raise forms.ValidationError(
                "Only Shapefiles and GeoTiffs are supported. You uploaded a %s file" %
                base_ext)
        if base_ext.lower() == ".shp":
            if dbf_file is None or shx_file is None:
                raise forms.ValidationError(
                    "When uploading Shapefiles, .shx and .dbf files are also required.")
            dbf_name, __ = os.path.splitext(dbf_file)
            shx_name, __ = os.path.splitext(shx_file)
            if dbf_name != base_name or shx_name != base_name:
                raise forms.ValidationError(
                    "It looks like you're uploading "
                    "components from different Shapefiles. Please "
                    "double-check your file selections.")
            if prj_file is not None:
                if os.path.splitext(prj_file)[0] != base_name:
                    raise forms.ValidationError(
                        "It looks like you're "
                        "uploading components from different Shapefiles. "
                        "Please double-check your file selections.")
            if xml_file is not None:
                if os.path.splitext(xml_file)[0] != base_name:
                    if xml_file.find('.shp') != -1:
                        # force rename of file so that file.shp.xml doesn't
                        # overwrite as file.shp
                        if cleaned.get("xml_file"):
                            cleaned["xml_file"].name = '%s.xml' % base_name

        return cleaned

    def write_files(self):

        absolute_base_file = None
        tempdir = tempfile.mkdtemp()

        if zipfile.is_zipfile(self.cleaned_data['base_file']):
            absolute_base_file = unzip_file(self.cleaned_data['base_file'], '.shp', tempdir=tempdir)

        else:
            for field in self.spatial_files:
                f = self.cleaned_data[field]
                if f is not None:
                    path = os.path.join(tempdir, f.name)
                    with open(path, 'wb') as writable:
                        for c in f.chunks():
                            writable.write(c)
            absolute_base_file = os.path.join(tempdir,
                                              self.cleaned_data["base_file"].name)
        return tempdir, absolute_base_file


class NewLayerUploadForm(LayerUploadForm):
    sld_file = forms.FileField(required=False)
    xml_file = forms.FileField(required=False)

    abstract = forms.CharField(required=False)
    layer_title = forms.CharField(required=False)
    permissions = JSONField()
    charset = forms.CharField(required=False)

    spatial_files = (
        "base_file",
        "dbf_file",
        "shx_file",
        "prj_file",
        "sld_file",
        "xml_file")

