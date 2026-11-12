# Mes hypothèses sur le process ADV

Je n'ai pas observé cette équipe ADV. Ce document liste mes hypothèses sur son
fonctionnement, ce que le prototype en fait, et les questions que je poserais à
l'équipe en immersion avant d'aller plus loin. Ce sont des hypothèses, pas des
faits : chacune peut être contredite par le terrain.

## Identification de la pharmacie

- Hypothèse : la pharmacie n'écrit presque jamais son code client. L'ADV la
  reconnaît à l'adresse de l'expéditeur, à la signature (nom et ville) ou à
  l'habitude.
- Dans le prototype : code client, ou nom et code postal, sinon exception. Je
  n'utilise pas l'adresse de l'expéditeur, volontairement.
- À valider : existe-t-il un identifiant stable côté pharmacie dans la fiche
  client ? Une adresse email est-elle fiable (boîtes partagées, groupements) ?

## Quantité hors colisage

- Hypothèse : les produits se vendent par colis complets. Une quantité hors
  colisage est une erreur de saisie ou une demande exceptionnelle, et l'ADV
  n'arrondit jamais sans l'accord de la pharmacie.
- Dans le prototype : refus, avec les deux multiples voisins proposés.
- À valider : y a-t-il des produits vendus à l'unité, des présentoirs, des
  lots ? Qui a le droit d'arrondir ?

## Remises et prix négociés

- Hypothèse : le prix vient du tarif et des conditions négociées avec la
  pharmacie ou son groupement (paliers, opérations promotionnelles, unités
  offertes). Un email peut citer une offre. Un agent ne doit jamais lire un prix
  dans un email : le prix reste celui de l'ERP.
- Dans le prototype : prix du catalogue uniquement, les remises sont hors
  périmètre.
- À valider : où vivent les conditions commerciales (ERP, tableur, mémoire du
  commercial) ? Qui tranche en cas d'écart ?

## Ruptures

- Hypothèse : celui qui lit l'email ne connaît pas le stock. En cas de rupture,
  l'ADV choisit entre livraison partielle avec reliquat, attente ou appel à la
  pharmacie, selon le client et le minimum de commande.
- Dans le prototype : le stock n'est pas regardé, c'est l'ERP qui gère la
  disponibilité après l'import.
- À valider : la règle de reliquat, et s'il existe un franco de port.

## Doublons et relances

- Hypothèse : les doublons viennent des relances (« avez-vous reçu ma
  commande ? »), des envois en copie à un commercial et des bons renvoyés
  corrigés. L'ADV les repère aujourd'hui de mémoire.
- Dans le prototype : non traité. Prochaine étape : un contrôle « commande déjà
  vue » (même client, même référence ou mêmes lignes à quelques jours d'écart)
  qui envoie en exception, sans jamais supprimer seul.
- À valider : la fréquence réelle, et comment distinguer une correction d'un
  doublon.

## Commandes transmises par un commercial

- Hypothèse : une partie des commandes arrive par un commercial terrain (email
  transféré, photo d'un bon, tableau). L'expéditeur n'est alors pas le client,
  le format change et des conditions particulières ont pu être accordées à
  l'oral.
- Dans le prototype : le client est identifié par le contenu de l'email, jamais
  par l'expéditeur, ce qui reste valable dans ce cas.
- À valider : la part des commandes passées par les commerciaux, et s'il existe
  un bon de commande standard.
