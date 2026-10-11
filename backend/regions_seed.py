"""Reference list of French wine regions and their main appellations (names only).

Intro texts and map images are not part of the repository: they are set per
installation through PUT /regions/{key} and POST /upload (see scripts/load_region_assets.py).
"""

REGIONS_SEED = [
    {"key": "bordelais", "name": "Bordelais", "appellations": [
        "Médoc", "Haut-Médoc", "Saint-Estèphe", "Pauillac", "Saint-Julien", "Margaux",
        "Blaye", "Côtes de Bourg", "Fronsac", "Pomerol", "Saint-Émilion",
        "Graves", "Pessac-Léognan", "Sauternes", "Entre-deux-Mers", "Loupiac", "Bordeaux"]},
    {"key": "sud-ouest", "name": "Sud-Ouest", "appellations": [
        "Bergerac", "Monbazillac", "Côtes du Marmandais", "Buzet", "Cahors", "Marcillac",
        "Gaillac", "Fronton", "Saint-Mont", "Madiran", "Pacherenc-du-Vic-Bilh", "Tursan", "Jurançon"]},
    {"key": "languedoc-roussillon", "name": "Languedoc-Roussillon", "appellations": [
        "Pic-Saint-Loup", "Terrasses du Larzac", "Faugères", "Saint-Chinian", "Cabardès", "Minervois",
        "Limoux", "Corbières", "Fitou", "Côtes du Roussillon", "Côtes du Roussillon Villages"]},
    {"key": "vallee-du-rhone", "name": "Vallée du Rhône", "appellations": [
        "Côte-Rôtie", "Condrieu", "Saint-Joseph", "Hermitage", "Crozes-Hermitage", "Cornas", "Saint-Péray",
        "Côtes-du-Rhône", "Côtes-du-Rhône-Villages", "Clairette de Die", "Cairanne", "Gigondas",
        "Vacqueyras", "Châteauneuf-du-Pape", "Ventoux", "Luberon", "Lirac", "Tavel", "Costières de Nîmes"]},
    {"key": "savoie-jura", "name": "Savoie et Jura", "appellations": [
        "Arbois", "Château-Chalon", "Côtes du Jura", "L'Étoile", "Chautagne", "Ayse", "Chignin", "Apremont", "Abymes"]},
    {"key": "beaujolais", "name": "Beaujolais", "appellations": [
        "Saint-Amour", "Juliénas", "Moulin-à-Vent", "Fleurie", "Chiroubles", "Morgon", "Côte-de-Brouilly",
        "Brouilly", "Beaujolais-Villages", "Beaujolais", "Coteaux du Lyonnais"]},
    {"key": "bourgogne", "name": "Bourgogne", "appellations": [
        "Chablis", "Saint-Bris", "Marsannay", "Nuits-Saint-Georges", "Aloxe-Corton", "Savigny-lès-Beaune",
        "Pommard", "Santenay", "Maranges", "Rully", "Mercurey", "Givry", "Montagny",
        "Viré-Clessé", "Mâcon", "Mâcon-Villages", "Saint-Véran", "Pouilly-Fuissé"]},
    {"key": "vallee-de-la-loire", "name": "Vallée de la Loire", "appellations": [
        "Muscadet", "Savennières", "Coteaux du Layon", "Anjou", "Saumur", "Chinon", "Bourgueil",
        "Saint-Nicolas-de-Bourgueil", "Vouvray", "Cheverny", "Valençay", "Coteaux du Giennois",
        "Sancerre", "Reuilly", "Pouilly-Fumé", "Quincy"]},
    {"key": "alsace", "name": "Alsace", "appellations": [
        "Alsace", "Alsace Grand Cru", "Crémant d'Alsace", "Riesling", "Gewurztraminer", "Pinot Gris",
        "Pinot Blanc", "Sylvaner", "Ribeauvillé", "Riquewihr", "Turckheim"]},
    {"key": "champagne", "name": "Champagne", "appellations": [
        "Champagne", "Montagne de Reims", "Vallée de la Marne", "Côte des Blancs", "Côte de Sézanne", "Côte des Bar"]},
]
