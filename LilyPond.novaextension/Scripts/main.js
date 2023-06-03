const issueCollection = new IssueCollection("LilyPond");

const messageRegex = new RegExp([
  "^([^:\\n\\r]+):",     // File path
  "(\\d+):(?:(\\d+):)?", // Line and column
  " (error|warning):",   // Message type
  " ([^\\n\\r]+)"        // Message
].join(""), "m");

exports.activate = function() {
    nova.workspace.onDidAddTextEditor(function(textEditor) {
        if (textEditor.document.syntax !== "lilypond") {
            return;
        }

        textEditor.onDidSave(function(textEditor) {
            const args = [
                "lilypond",
                "--loglevel=WARNING",
                `--output=${nova.path.dirname(textEditor.document.path)}/${nova.path.splitext(textEditor.document.path)[0]}`,
                textEditor.document.path
            ];

            const options = {
                args: args,
                cwd: nova.workspace.path,
                stdio: ["ignore", "ignore", "pipe"]
            };

            const process = new Process("/usr/bin/env", options);

            process.onStderr(function(line) {
                console.log(line.trimEnd());

                const result = messageRegex.exec(line);
                if (result) {
                    const issue = new Issue();
                    issue.source = "LilyPond";
                    issue.line = Number.parseInt(result[2], 10);
                    const reportedColumn = result[3];
                    issue.column = reportedColumn ? Number.parseInt(reportedColumn, 10) : 1;
                    issue.severity = result[4] === "error" ? IssueSeverity.Error : IssueSeverity.Warning;
                    issue.message = [result[5]];

                    issueCollection.append(`file://${result[1]}`, [issue]);
                }
            });

            issueCollection.clear();

            process.start();
        });
    });
};

exports.deactivate = function() {
    issueCollection.dispose();
};
