from django.db import models


class Controller(models.Model):
    home_id = models.CharField(primary_key=True, unique=True, max_length=60)
    name = models.CharField(verbose_name="Non", blank=True, null=True, max_length=120)
    product = models.CharField(verbose_name="Non", blank=True, null=True, max_length=120)

    def __str__(self):
        """ display name in shell"""
        return self.name

    class META:
        verbose_name = "Contrôleur"


class Node(models.Model):
    controller_node = models.ForeignKey(Controller, on_delete=models.CASCADE, related_name='controller')
    node_id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(verbose_name="Nom", blank=True, null=True, max_length=120)
    location = models.CharField(verbose_name="Localisation", blank=True, null=True, max_length=120)
    product_type = models.CharField(verbose_name="Type de produit", max_length=10)
    product_name = models.CharField(verbose_name="Nom du produit", max_length=120)
    manufacturer_name = models.CharField(verbose_name="Fabriquant", max_length=120)
    num_groups = models.IntegerField(verbose_name="N° de groupe", blank=True, null=True)
    is_beaming_device = models.BooleanField(verbose_name="Bon état")
    is_failed = models.BooleanField(verbose_name="Manquant")
    is_ready = models.BooleanField(verbose_name="Prêt")
    is_awake = models.BooleanField(verbose_name="Réveillé")

    def __str__(self):
        """ display name in shell"""
        return "id : {}, nom du produit: {}".format(self.node_id, self.product_name)

    class META:
        verbose_name = "Noeuds"
        constraints = [
            models.UniqueConstraint(fields=['controller_node', ' node_id'], name='unique_controller_node_id')
        ]


class Params(models.Model):
    node_param = models.ForeignKey(Node, on_delete=models.CASCADE)
    index = models.IntegerField()
    label = models.CharField(verbose_name="Nom du paramètre", max_length=120)
    data = models.CharField(verbose_name="Paramètre actuel", max_length=120)

    def __str__(self):
        """ display name in shell"""
        return "{} : {} ".format(self.index, self.label)

    class META:
        verbose_name = "Paramètres"
        constraints = [
            models.UniqueConstraint(fields=['node', 'index'], name='node_value_id')
        ]


class Instances(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    index = models.IntegerField()
    value_id = models.IntegerField(primary_key=True, unique=True,)
    type = models.CharField(verbose_name="Type d'instance", max_length=120)
    name = models.CharField(verbose_name="Nom", blank=True, null=True, max_length=120)
    location = models.CharField(verbose_name="Pièce", blank=True, null=True, max_length=120)
    level = models.IntegerField(blank=True, null=True)
    state = models.CharField(verbose_name='status', max_length=10)

    def __str__(self):
        """ display name in shell"""
        return "{} : {} ".format(self.index, self.type)

    class META:
        verbose_name = "Instances"
        constraints = [
            models.UniqueConstraint(fields=['node', 'value_id'], name='node_value_id')
        ]
