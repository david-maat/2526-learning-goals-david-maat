const learningGoalAssets = import.meta.glob('../../learning_goals/*/*/assets/**/*', {
    eager: true,
    query: '?url',
    import: 'default'
}) as Record<string, string>;

const staticContentAssets = import.meta.glob('../../static/content/*/*/assets/**/*', {
    eager: true,
    query: '?url',
    import: 'default'
}) as Record<string, string>;

export const assets: Record<string, string> = {
    ...learningGoalAssets,
    ...staticContentAssets,
};

export function resolveAssetPath(categoryNumber: number, goalNumber: string, filename: string): string | null {
    // Normalize common relative formats used in evidence files.
    const normalizedFilename = filename
        .replace(/^[./\\]+/, '')
        .replace(/^assets[\\/]+/, '')
        .replace(/\\/g, '/');

    const learningGoalsKey = `../../learning_goals/${categoryNumber}/${goalNumber}/assets/${normalizedFilename}`;
    const staticContentKey = `../../static/content/${categoryNumber}/${goalNumber}/assets/${normalizedFilename}`;

    return assets[learningGoalsKey] || assets[staticContentKey] || null;
}
