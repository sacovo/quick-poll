const userPk = document.querySelector("#userPk").value;

const store = PetiteVue.reactive({
  $delimiters: ["${", "}"],
  voteData: {},
  pastData: [],
  question: "",
  options: "",
  userOption: null,

  get hasOpenVote() {
    return Object.entries(this.voteData).length > 0;
  },

  refresh() {
    fetchData().then((data) => {
      this.voteData = data;
      this.userOption = null;
      if (!this.voteData.answers) return;
      for (answer of this.voteData.answers) {
        if (answer["delegate__user__pk"] == userPk) {
          this.userOption = answer["option"];
          break;
        }
      }
    });
  },

  refreshPast() {
    fetchPast().then((data) => (this.pastData = data));
  },

  voteAction(event) {
    const optionId = event.target.dataset.id;
    postData("/vote/", { option: optionId });
  },

  openVote(event) {
    if (this.question && this.options) {
      postData("/open/", { question: this.question, options: this.options });
      this.question = "";
      this.options = "";
    }
  },

  closeVote(event) {
    postData("/close/", {});
  },
});

store.refresh();
store.refreshPast();

setInterval(() => store.refresh(), 500);
setInterval(() => store.refreshPast(), 2000);

PetiteVue.createApp(store).mount();
